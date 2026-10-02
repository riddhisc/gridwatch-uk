from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, Request

from app.clients.octopus import OctopusEnergyClient
from app.config import get_settings
from app.core.errors import utcnow
from app.repositories.snapshots import SnapshotRepository
from app.schemas.api import PricePoint
from app.services.overview import price_point

router = APIRouter(prefix="/v1/prices", tags=["prices"])
repo = SnapshotRepository()


async def _live_rates(
    request: Request, *, period_from: datetime, period_to: datetime
) -> tuple[list, str, str, str]:
    settings = get_settings()
    client: OctopusEnergyClient = request.app.state.octopus_client
    product_code = settings.octopus_default_product_code.strip()
    if not product_code:
        product = await client.discover_current_agile_product()
        if product is None:
            raise HTTPException(status_code=502, detail="No current Agile product found")
        product_code = product.code
    region = settings.octopus_default_gsp_region
    tariff = client.tariff_code_for(product_code, region)
    rates = await client.get_standard_unit_rates(
        product_code=product_code,
        tariff_code=tariff,
        period_from=period_from,
        period_to=period_to,
    )
    return rates, product_code, tariff, region


def _rate_points(rates, product_code: str, tariff: str, region: str) -> list[PricePoint]:
    points: list[PricePoint] = []
    for rate in rates:
        if rate.valid_to is None:
            continue
        points.append(
            PricePoint(
                period_from=rate.valid_from,
                period_to=rate.valid_to,
                value_exc_vat=rate.value_exc_vat,
                value_inc_vat=rate.value_inc_vat,
                product_code=product_code,
                tariff_code=tariff,
                gsp_region=region,
            )
        )
    return sorted(points, key=lambda item: item.period_from)


@router.get("/current", response_model=PricePoint)
async def current_price(request: Request) -> PricePoint:
    now = utcnow()
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is not None:
        async with session_factory() as session:
            rows = await repo.list_prices(
                session,
                tariff_code=None,
                start=now - timedelta(hours=2),
                end=now + timedelta(hours=2),
            )
        for row in rows:
            if row.period_from <= now < row.period_to:
                return price_point(row)

    rates, product_code, tariff, region = await _live_rates(
        request,
        period_from=now - timedelta(hours=12),
        period_to=now + timedelta(hours=24),
    )
    points = _rate_points(rates, product_code, tariff, region)
    for point in points:
        if point.period_from <= now < point.period_to:
            return point
    if points:
        upcoming = [p for p in points if p.period_from >= now]
        return upcoming[0] if upcoming else points[-1]
    raise HTTPException(status_code=404, detail="No Agile unit rate for the current half-hour")


@router.get("/history", response_model=list[PricePoint])
async def price_history(
    request: Request,
    hours: int = Query(default=24, ge=1, le=168),
) -> list[PricePoint]:
    now = utcnow()
    start = now - timedelta(hours=hours)
    end = now + timedelta(hours=hours)
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is not None:
        async with session_factory() as session:
            rows = await repo.list_prices(session, tariff_code=None, start=start, end=end)
        if rows:
            return [price_point(row) for row in rows]
    rates, product_code, tariff, region = await _live_rates(
        request, period_from=start, period_to=end
    )
    return _rate_points(rates, product_code, tariff, region)
