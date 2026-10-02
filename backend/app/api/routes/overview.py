from __future__ import annotations

import asyncio
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Query, Request

from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.octopus import OctopusEnergyClient
from app.config import get_settings
from app.core.errors import UpstreamAPIError, utcnow
from app.core.logging import get_logger
from app.db.models import CarbonSnapshot, PriceSnapshot
from app.repositories.snapshots import SnapshotRepository
from app.schemas.api import LocationView, OverviewResponse
from app.schemas.carbon import RegionalLocationBlock, RegionalLocationResponse
from app.services.advice import build_advice
from app.services.overview import assemble_overview
from app.services.places import (
    GSP_NAMES,
    Place,
    display_name,
    grid_note_for,
    grid_region_for,
    resolve_query,
    shared_area_names,
)
from app.services.snapshot_builder import carbon_value

router = APIRouter(prefix="/v1", tags=["dashboard"])
repo = SnapshotRepository()
logger = get_logger(__name__)


def _from_intensity(periods, *, region_code: str = "GB", region_name: str | None = None) -> list[CarbonSnapshot]:
    rows: list[CarbonSnapshot] = []
    for period in periods:
        rows.append(
            CarbonSnapshot(
                period_from=period.from_,
                period_to=period.to,
                region_code=region_code,
                region_name=region_name,
                forecast_intensity=period.intensity.forecast,
                actual_intensity=period.intensity.actual,
                intensity_index=period.intensity.index,
                generation_mix=[{"fuel": item.fuel, "perc": item.perc} for item in period.generationmix]
                if getattr(period, "generationmix", None)
                else None,
            )
        )
    return rows


def _from_regional_block(block: RegionalLocationBlock) -> list[CarbonSnapshot]:
    region_code = str(block.regionid)
    return _from_intensity(block.data, region_code=region_code, region_name=block.shortname)


def _require_regional_block(
    response: RegionalLocationResponse, *, status_code: int, detail: str
) -> RegionalLocationBlock:
    if not response.data:
        raise HTTPException(status_code=status_code, detail=detail)
    return response.data[0]


def _from_rates(rates, product_code: str, tariff: str, region: str) -> list[PriceSnapshot]:
    rows: list[PriceSnapshot] = []
    for rate in rates:
        if rate.valid_to is None:
            continue
        rows.append(
            PriceSnapshot(
                period_from=rate.valid_from,
                period_to=rate.valid_to,
                product_code=product_code,
                tariff_code=tariff,
                gsp_region=region,
                value_exc_vat=rate.value_exc_vat,
                value_inc_vat=rate.value_inc_vat,
            )
        )
    return rows


async def _load_agile_rates(
    octopus: OctopusEnergyClient, *, gsp_region: str, start, end
) -> list[PriceSnapshot]:
    settings = get_settings()
    product_code = settings.octopus_default_product_code.strip()
    if not product_code:
        product = await octopus.discover_current_agile_product()
        product_code = product.code if product else ""
    if not product_code:
        return []
    tariff = octopus.tariff_code_for(product_code, gsp_region)
    rates = await octopus.get_standard_unit_rates(
        product_code=product_code,
        tariff_code=tariff,
        period_from=start,
        period_to=end,
    )
    return _from_rates(rates, product_code, tariff, gsp_region)


@router.get("/overview", response_model=OverviewResponse)
async def overview(
    request: Request,
    city: str | None = Query(default=None),
    area: str | None = Query(default=None),
    postcode: str | None = Query(default=None),
) -> OverviewResponse:
    place: Place = resolve_query(city=city, area=area, postcode=postcode)
    now = utcnow()
    start = now - timedelta(hours=24)
    end = now + timedelta(hours=48)
    carbon_client: CarbonIntensityClient = request.app.state.carbon_client
    octopus: OctopusEnergyClient = request.app.state.octopus_client

    regional = bool(place.outward_postcode)
    city_id = place.parent_id or place.id
    area_id = place.id.removeprefix(f"{city_id}-") if place.parent_id else None
    location = LocationView(
        id=city_id,
        label=display_name(place),
        postcode=place.outward_postcode or None,
        scope="regional" if regional else "national",
        neso_region="Great Britain" if not regional else None,
        city_id=city_id,
        area_id=area_id,
    )

    carbon_rows: list[CarbonSnapshot] = []
    price_rows: list[PriceSnapshot] = []
    gsp_region = get_settings().octopus_default_gsp_region

    if regional:
        try:
            current_resp, past_resp, ahead_resp, gsp = await asyncio.gather(
                carbon_client.get_regional_by_postcode(place.outward_postcode),
                carbon_client.get_regional_past_24h_by_postcode(now, place.outward_postcode),
                carbon_client.get_regional_forecast_48h_by_postcode(now, place.outward_postcode),
                octopus.get_grid_supply_point(place.lookup_postcode or place.outward_postcode),
            )
            current_block = _require_regional_block(
                current_resp,
                status_code=404,
                detail=f"No NESO regional carbon data for postcode {place.outward_postcode}",
            )
            past = _require_regional_block(
                past_resp,
                status_code=502,
                detail="NESO regional carbon history returned no periods",
            )
            ahead = _require_regional_block(
                ahead_resp,
                status_code=502,
                detail="NESO regional carbon forecast returned no periods",
            )
        except UpstreamAPIError as exc:
            status = 404 if exc.status_code == 400 else 502
            raise HTTPException(
                status_code=status,
                detail=f"NESO regional carbon lookup failed for {place.outward_postcode}",
            ) from exc
        carbon_rows = _from_regional_block(past) + _from_regional_block(ahead)
        unique: dict = {}
        for row in carbon_rows:
            unique[row.period_from] = row
        carbon_rows = list(unique.values())
        location.neso_region = current_block.shortname
        location.neso_region_id = current_block.regionid
        location.postcode = current_block.postcode or place.outward_postcode
        grid_label = grid_region_for(place) or current_block.shortname
        location.shared_with = shared_area_names(place, grid_label)
        location.grid_note = grid_note_for(place, grid_label)
        if gsp:
            gsp_region = gsp
        location.gsp_region = gsp_region
        location.gsp_name = GSP_NAMES.get(gsp_region.upper())
        price_rows = await _load_agile_rates(octopus, gsp_region=gsp_region, start=start, end=end)
        overview_data = assemble_overview(
            carbon_rows=carbon_rows, price_rows=price_rows, now=now, location=location
        )
        if current_block.data:
            latest = current_block.data[0]
            overview_data.current.period_from = latest.from_
            overview_data.current.period_to = latest.to
            overview_data.current.forecast = latest.intensity.forecast
            overview_data.current.actual = latest.intensity.actual
            overview_data.current.index = latest.intensity.index
            overview_data.current.region_code = str(current_block.regionid)
            overview_data.current.region_name = current_block.shortname
            overview_data.generation.mix = latest.generationmix
            overview_data.generation.period_from = latest.from_
            overview_data.generation.period_to = latest.to
            overview_data.advice = build_advice(
                index=latest.intensity.index,
                carbon=carbon_value(latest.intensity.actual, latest.intensity.forecast),
                price_inc_vat=(
                    overview_data.current_price.value_inc_vat if overview_data.current_price else None
                ),
            )
        return overview_data

    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is not None:
        async with session_factory() as session:
            carbon_rows = await repo.list_carbon(session, region_code="GB", start=start, end=end)
            price_rows = await repo.list_prices(session, tariff_code=None, start=start, end=end)

    if not carbon_rows:
        past = await carbon_client.get_past_24h(now)
        ahead = await carbon_client.get_forecast_48h(now)
        carbon_rows = _from_intensity(past.data + ahead.data, region_name="Great Britain")

    if not price_rows:
        price_rows = await _load_agile_rates(octopus, gsp_region=gsp_region, start=start, end=end)

    location.gsp_region = gsp_region
    location.gsp_name = GSP_NAMES.get(gsp_region.upper())
    overview_data = assemble_overview(
        carbon_rows=carbon_rows, price_rows=price_rows, now=now, location=location
    )
    try:
        live, mix = await asyncio.gather(
            carbon_client.get_current_intensity(),
            carbon_client.get_generation_mix(),
        )
        if live.data:
            period = live.data[0]
            overview_data.current.period_from = period.from_
            overview_data.current.period_to = period.to
            overview_data.current.forecast = period.intensity.forecast
            overview_data.current.actual = period.intensity.actual
            overview_data.current.index = period.intensity.index
            overview_data.advice = build_advice(
                index=period.intensity.index,
                carbon=carbon_value(period.intensity.actual, period.intensity.forecast),
                price_inc_vat=(
                    overview_data.current_price.value_inc_vat if overview_data.current_price else None
                ),
            )
        if mix.data:
            overview_data.generation.period_from = mix.data[0].from_
            overview_data.generation.period_to = mix.data[0].to
            overview_data.generation.mix = mix.data[0].generationmix
    except Exception:
        logger.warning("live_current_overlay_failed", exc_info=True)
    return overview_data
