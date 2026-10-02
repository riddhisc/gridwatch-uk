from datetime import UTC, datetime, timedelta

from app.db.models import CarbonSnapshot, PriceSnapshot
from app.schemas.carbon import IntensityPeriod
from app.services.advice import build_advice
from app.services.overview import assemble_overview
from app.services.snapshot_builder import intensity_rows


def test_advice_green_and_cheap() -> None:
    advice = build_advice(index="low", carbon=51, price_inc_vat=-0.3)
    assert advice.action == "charge_now"
    assert "excellent" in advice.headline.lower()


def test_advice_dirty_grid() -> None:
    advice = build_advice(index="high", carbon=280, price_inc_vat=32)
    assert advice.action == "wait"


def test_intensity_rows_from_periods() -> None:
    period = IntensityPeriod.model_validate(
        {
            "from": "2026-09-19T08:00Z",
            "to": "2026-09-19T08:30Z",
            "intensity": {"forecast": 50, "actual": 51, "index": "low"},
        }
    )
    rows = intensity_rows([period])
    assert rows[0]["actual_intensity"] == 51
    assert rows[0]["region_code"] == "GB"


def test_overview_picks_best_window() -> None:
    now = datetime(2026, 9, 19, 9, 0, tzinfo=UTC)
    carbon = []
    prices = []
    for i in range(6):
        start = now + timedelta(minutes=30 * i)
        end = start + timedelta(minutes=30)
        carbon.append(
            CarbonSnapshot(
                period_from=start,
                period_to=end,
                region_code="GB",
                forecast_intensity=80 if i != 2 else 40,
                actual_intensity=None,
                intensity_index="low",
            )
        )
        prices.append(
            PriceSnapshot(
                period_from=start,
                period_to=end,
                product_code="AGILE-24-10-01",
                tariff_code="E-1R-AGILE-24-10-01-C",
                gsp_region="C",
                value_exc_vat=10 if i != 2 else -2,
                value_inc_vat=10.5 if i != 2 else -2.1,
            )
        )
    overview = assemble_overview(carbon_rows=carbon, price_rows=prices, now=now)
    assert overview.best_window is not None
    assert overview.best_window.carbon == 40
    assert overview.advice.action in {"charge_now", "use_now", "ok", "wait"}
