from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.core.errors import utcnow
from app.db.models import CarbonSnapshot, PriceSnapshot
from app.ml.inference import get_recommendations
from app.schemas.api import (
    Advice,
    BestWindow,
    CarbonPoint,
    CombinedPoint,
    CurrentCarbonView,
    CurrentGenerationView,
    LocationView,
    OverviewResponse,
    PricePoint,
)
from app.schemas.carbon import GenerationFuelShare
from app.services.advice import build_advice
from app.services.snapshot_builder import carbon_value


def _mix(value: Any) -> list[GenerationFuelShare]:
    if not value:
        return []
    if isinstance(value, list):
        return [GenerationFuelShare.model_validate(item) for item in value]
    return []


def carbon_point(row: CarbonSnapshot) -> CarbonPoint:
    return CarbonPoint(
        period_from=row.period_from,
        period_to=row.period_to,
        forecast=row.forecast_intensity,
        actual=row.actual_intensity,
        index=row.intensity_index,
        generation_mix=_mix(row.generation_mix),
    )


def price_point(row: PriceSnapshot) -> PricePoint:
    return PricePoint(
        period_from=row.period_from,
        period_to=row.period_to,
        value_exc_vat=float(row.value_exc_vat),
        value_inc_vat=float(row.value_inc_vat),
        product_code=row.product_code,
        tariff_code=row.tariff_code,
        gsp_region=row.gsp_region,
    )


def _current_period(points: list[CarbonPoint], now: datetime) -> CarbonPoint | None:
    for point in points:
        if point.period_from <= now < point.period_to:
            return point
    return points[-1] if points else None


def _current_price(points: list[PricePoint], now: datetime) -> PricePoint | None:
    for point in points:
        if point.period_from <= now < point.period_to:
            return point
    upcoming = [p for p in points if p.period_from >= now]
    return upcoming[0] if upcoming else None


def score_window(carbon: int | None, price: float | None) -> float | None:
    if carbon is None and price is None:
        return None
    carbon_part = min((carbon or 250) / 400.0, 1.5)
    price_part = min((float(price or 20) + 20.0) / 80.0, 1.5)
    return 0.65 * carbon_part + 0.35 * price_part


def pick_best_window(combined: list[CombinedPoint], now: datetime) -> BestWindow | None:
    horizon = now + timedelta(hours=24)
    ranked: list[tuple[float, CombinedPoint]] = []
    for point in combined:
        if point.period_from < now or point.period_from >= horizon:
            continue
        score = score_window(point.carbon, point.price_inc_vat)
        if score is None:
            continue
        ranked.append((score, point))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0])
    winner = ranked[0][1]
    bits = []
    if winner.carbon is not None:
        bits.append(f"{winner.carbon} gCO₂/kWh")
    if winner.price_inc_vat is not None:
        bits.append(f"{winner.price_inc_vat:.1f}p/kWh")
    return BestWindow(
        period_from=winner.period_from,
        period_to=winner.period_to,
        carbon=winner.carbon,
        price_inc_vat=winner.price_inc_vat,
        reason="Lowest combined carbon + Agile price in the next 24 hours"
        + (f" ({', '.join(bits)})" if bits else ""),
    )


def assemble_overview(
    *,
    carbon_rows: list[CarbonSnapshot],
    price_rows: list[PriceSnapshot],
    now: datetime | None = None,
    location: LocationView | None = None,
) -> OverviewResponse:
    now = now or utcnow()
    carbon_points = [carbon_point(row) for row in carbon_rows]
    price_points = [price_point(row) for row in price_rows]
    current = _current_period(carbon_points, now)
    live_price = _current_price(price_points, now)

    history = [p for p in carbon_points if p.period_to <= now]
    forecast = [p for p in carbon_points if p.period_from >= now]
    if current and current not in forecast:
        forecast = [current, *forecast]

    price_by_start = {p.period_from: p for p in price_points}
    combined: list[CombinedPoint] = []
    for point in carbon_points:
        price = price_by_start.get(point.period_from)
        combined.append(
            CombinedPoint(
                period_from=point.period_from,
                period_to=point.period_to,
                carbon=carbon_value(point.actual, point.forecast),
                price_inc_vat=price.value_inc_vat if price else None,
                index=point.index,
            )
        )

    carbon_now = carbon_value(current.actual, current.forecast) if current else None
    advice: Advice = build_advice(
        index=current.index if current else None,
        carbon=carbon_now,
        price_inc_vat=live_price.value_inc_vat if live_price else None,
    )

    mix = current.generation_mix if current else []
    resolved = location or LocationView(
        id="gb",
        label="Great Britain (national)",
        scope="national",
        neso_region="Great Britain",
    )
    current_view = CurrentCarbonView(
        period_from=current.period_from if current else now,
        period_to=current.period_to if current else now,
        forecast=current.forecast if current else None,
        actual=current.actual if current else None,
        index=current.index if current else None,
        region_code=(
            str(resolved.neso_region_id) if resolved.neso_region_id else "GB"
        ),
        region_name=resolved.neso_region or resolved.label,
        cached=False,
    )
    generation = CurrentGenerationView(
        period_from=current_view.period_from,
        period_to=current_view.period_to,
        mix=mix,
        cached=False,
    )

    return OverviewResponse(
        advice=advice,
        location=resolved,
        current=current_view,
        generation=generation,
        current_price=live_price,
        forecast=forecast,
        history=history[-96:],
        prices=price_points,
        combined=combined,
        best_window=pick_best_window(combined, now),
        recommendations=get_recommendations(),
        as_of=now,
    )
