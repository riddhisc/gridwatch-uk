from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query, Request

from app.clients.carbon_intensity import CarbonIntensityClient
from app.config import get_settings
from app.core.errors import UpstreamAPIError, utcnow
from app.repositories.snapshots import SnapshotRepository
from app.schemas.api import CarbonPoint, CurrentCarbonView, CurrentGenerationView
from app.schemas.carbon import GenerationResponse, IntensityResponse
from app.services.overview import carbon_point

router = APIRouter(prefix="/v1/carbon", tags=["carbon"])
repo = SnapshotRepository()


async def _cached_json(request: Request, key: str, fetcher, ttl: int):
    cache = request.app.state.cache
    try:
        payload, cached = await cache.get_or_set(key, fetcher, ttl)
        return payload, cached
    except UpstreamAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/current", response_model=CurrentCarbonView)
async def current_carbon(request: Request) -> CurrentCarbonView:
    settings = get_settings()
    client: CarbonIntensityClient = request.app.state.carbon_client

    async def fetch() -> dict:
        response = await client.get_current_intensity()
        return response.model_dump(mode="json", by_alias=True)

    payload, cached = await _cached_json(request, "upstream:carbon:current", fetch, settings.cache_ttl_carbon_seconds)
    parsed = IntensityResponse.model_validate(payload)
    if not parsed.data:
        raise HTTPException(status_code=502, detail="Carbon Intensity API returned no periods")
    period = parsed.data[0]
    return CurrentCarbonView(
        period_from=period.from_,
        period_to=period.to,
        forecast=period.intensity.forecast,
        actual=period.intensity.actual,
        index=period.intensity.index,
        cached=cached,
    )


@router.get("/generation", response_model=CurrentGenerationView)
async def current_generation(request: Request) -> CurrentGenerationView:
    settings = get_settings()
    client: CarbonIntensityClient = request.app.state.carbon_client

    async def fetch() -> dict:
        response = await client.get_generation_mix()
        return response.model_dump(mode="json", by_alias=True)

    payload, cached = await _cached_json(
        request, "upstream:carbon:generation", fetch, settings.cache_ttl_carbon_seconds
    )
    parsed = GenerationResponse.model_validate(payload)
    if not parsed.data:
        raise HTTPException(status_code=502, detail="Generation mix API returned no periods")
    period = parsed.data[0]
    return CurrentGenerationView(
        period_from=period.from_,
        period_to=period.to,
        mix=period.generationmix,
        cached=cached,
    )


@router.get("/forecast", response_model=list[CarbonPoint])
async def carbon_forecast(request: Request) -> list[CarbonPoint]:
    """NESO 48-hour carbon intensity forecast."""
    settings = get_settings()
    client: CarbonIntensityClient = request.app.state.carbon_client

    async def fetch() -> dict:
        response = await client.get_forecast_48h(utcnow())
        return response.model_dump(mode="json", by_alias=True)

    payload, _cached = await _cached_json(
        request, "upstream:carbon:fw48h", fetch, settings.cache_ttl_carbon_seconds
    )
    parsed = IntensityResponse.model_validate(payload)
    return [
        CarbonPoint(
            period_from=period.from_,
            period_to=period.to,
            forecast=period.intensity.forecast,
            actual=period.intensity.actual,
            index=period.intensity.index,
        )
        for period in parsed.data
    ]


@router.get("/history", response_model=list[CarbonPoint])
async def carbon_history(
    request: Request,
    hours: int = Query(default=24, ge=1, le=168),
    region: str = Query(default="GB"),
) -> list[CarbonPoint]:
    now = utcnow()
    start = now - timedelta(hours=hours)
    session_factory = getattr(request.app.state, "session_factory", None)
    rows = []
    if session_factory is not None:
        async with session_factory() as session:
            rows = await repo.list_carbon(session, region_code=region, start=start, end=now)
    if rows:
        return [carbon_point(row) for row in rows]

    client: CarbonIntensityClient = request.app.state.carbon_client
    try:
        if region.strip().upper() == "GB":
            live = await client.get_intensity_range(start, now)
            periods = live.data
        else:
            try:
                region_id = int(region)
            except ValueError as exc:
                raise HTTPException(
                    status_code=400, detail="region must be GB or a NESO region id"
                ) from exc
            live = await client.get_regional_intensity_range_by_region_id(start, now, region_id)
            if not live.data:
                return []
            periods = live.data[0].data
    except UpstreamAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return [
        CarbonPoint(
            period_from=period.from_,
            period_to=period.to,
            forecast=period.intensity.forecast,
            actual=period.intensity.actual,
            index=period.intensity.index,
        )
        for period in periods
    ]
