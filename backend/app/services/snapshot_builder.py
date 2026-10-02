from __future__ import annotations

from app.schemas.carbon import GenerationFuelShare, GenerationPeriod, IntensityPeriod
from app.schemas.octopus import UnitRate


def intensity_rows(periods: list[IntensityPeriod], *, region_code: str = "GB") -> list[dict]:
    rows: list[dict] = []
    for period in periods:
        rows.append(
            {
                "period_from": period.from_,
                "period_to": period.to,
                "region_code": region_code,
                "region_name": "Great Britain",
                "forecast_intensity": period.intensity.forecast,
                "actual_intensity": period.intensity.actual,
                "intensity_index": period.intensity.index,
                "generation_mix": None,
                "source": "neso_carbon_intensity",
            }
        )
    return rows


def mix_payload(shares: list[GenerationFuelShare]) -> list[dict]:
    return [{"fuel": item.fuel, "perc": item.perc} for item in shares]


def generation_mix_updates(periods: list[GenerationPeriod], *, region_code: str = "GB") -> list[dict]:
    updates: list[dict] = []
    for period in periods:
        updates.append(
            {
                "period_from": period.from_,
                "period_to": period.to,
                "region_code": region_code,
                "generation_mix": mix_payload(period.generationmix),
            }
        )
    return updates


def price_rows(
    rates: list[UnitRate],
    *,
    product_code: str,
    tariff_code: str,
    gsp_region: str,
) -> list[dict]:
    rows: list[dict] = []
    for rate in rates:
        end = rate.valid_to
        if end is None:
            continue
        rows.append(
            {
                "period_from": rate.valid_from,
                "period_to": end,
                "product_code": product_code,
                "tariff_code": tariff_code,
                "gsp_region": gsp_region,
                "value_exc_vat": rate.value_exc_vat,
                "value_inc_vat": rate.value_inc_vat,
                "source": "octopus_agile",
            }
        )
    return rows


def carbon_value(actual: int | None, forecast: int | None) -> int | None:
    if actual is not None:
        return actual
    return forecast
