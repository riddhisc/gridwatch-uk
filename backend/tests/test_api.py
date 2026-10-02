from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api import api_router


class MemoryCache:
    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    async def ping(self) -> bool:
        return True

    async def get_or_set(self, key: str, factory, ttl_seconds: int):
        if key in self.store:
            return self.store[key], True
        value = await factory()
        self.store[key] = value
        return value, False


class FakeCarbonClient:
    async def get_current_intensity(self):
        from app.schemas.carbon import IntensityResponse

        return IntensityResponse.model_validate(
            {
                "data": [
                    {
                        "from": "2026-09-19T08:00Z",
                        "to": "2026-09-19T08:30Z",
                        "intensity": {"forecast": 90, "actual": 88, "index": "low"},
                    }
                ]
            }
        )

    async def get_generation_mix(self):
        from app.schemas.carbon import GenerationResponse

        return GenerationResponse.model_validate(
            {
                "data": {
                    "from": "2026-09-19T08:00Z",
                    "to": "2026-09-19T08:30Z",
                    "generationmix": [{"fuel": "wind", "perc": 64.7}, {"fuel": "gas", "perc": 10.4}],
                }
            }
        )

    async def get_forecast_48h(self, start):
        return await self.get_current_intensity()

    async def get_past_24h(self, start):
        return await self.get_current_intensity()

    async def get_intensity_range(self, start, end):
        self.last_intensity_range = (start, end)
        return await self.get_current_intensity()

    async def get_regional_intensity_range_by_region_id(self, start, end, region_id: int):
        self.last_regional_range = (start, end, region_id)
        return await self.get_regional_by_postcode(str(region_id))

    async def get_regional_by_postcode(self, postcode: str):
        from app.schemas.carbon import RegionalLocationResponse

        return RegionalLocationResponse.model_validate(
            {
                "data": [
                    {
                        "regionid": 3,
                        "dnoregion": "Electricity North West",
                        "shortname": "North West England",
                        "postcode": postcode,
                        "data": [
                            {
                                "from": "2026-09-19T08:00Z",
                                "to": "2026-09-19T08:30Z",
                                "intensity": {"forecast": 2, "index": "very low"},
                                "generationmix": [{"fuel": "wind", "perc": 72.8}],
                            }
                        ],
                    }
                ]
            }
        )

    async def get_regional_forecast_48h_by_postcode(self, start, postcode: str):
        return await self.get_regional_by_postcode(postcode)

    async def get_regional_past_24h_by_postcode(self, start, postcode: str):
        return await self.get_regional_by_postcode(postcode)


class FakeOctopusClient:
    def tariff_code_for(self, product_code: str, gsp_region: str) -> str:
        return f"E-1R-{product_code}-{gsp_region}"

    async def discover_current_agile_product(self):
        from app.schemas.octopus import ProductSummary

        return ProductSummary(code="AGILE-24-10-01", display_name="Agile Octopus")

    async def get_standard_unit_rates(self, **kwargs):
        from app.schemas.octopus import UnitRate

        self.last_rate_window = (kwargs.get("period_from"), kwargs.get("period_to"))
        return [
            UnitRate.model_validate(
                {
                    "value_exc_vat": -2.0,
                    "value_inc_vat": -2.1,
                    "valid_from": "2026-09-19T08:00:00Z",
                    "valid_to": "2026-09-19T08:30:00Z",
                }
            )
        ]

    async def get_grid_supply_point(self, postcode: str) -> str:
        return "G"


def build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    app.state.cache = MemoryCache()
    app.state.session_factory = None
    app.state.carbon_client = FakeCarbonClient()
    app.state.octopus_client = FakeOctopusClient()
    return app


@pytest.mark.asyncio
async def test_health_ok_without_database() -> None:
    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "green-power-hours-api"
    assert body["checks"]["database"] == "skipped"
    assert body["checks"]["redis"] == "ok"
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_current_carbon_and_ml_degradation() -> None:
    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        carbon = await client.get("/v1/carbon/current")
        recs = await client.get("/v1/recommendations")
        forecast = await client.get("/v1/forecast")
        summary = await client.get("/v1/summary")

    assert carbon.status_code == 200
    assert carbon.json()["actual"] == 88
    assert recs.json()["available"] is False
    assert forecast.json()["feature"] == "forecast"
    assert summary.json()["reason"] == "not_yet_available"


@pytest.mark.asyncio
async def test_overview_and_neso_forecast_are_not_ml() -> None:
    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        overview = await client.get("/v1/overview")
        forecast = await client.get("/v1/carbon/forecast")
        prices = await client.get("/v1/prices/current")

    assert overview.status_code == 200
    body = overview.json()
    assert body["current"]["actual"] == 88
    assert body["advice"]["headline"]
    assert body["recommendations"]["available"] is False
    assert forecast.status_code == 200
    assert forecast.json()[0]["forecast"] == 90
    assert prices.status_code == 200
    assert prices.json()["value_inc_vat"] == -2.1


@pytest.mark.asyncio
async def test_overview_city_uses_regional_grid() -> None:
    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        places = await client.get("/v1/locations")
        overview = await client.get("/v1/overview", params={"city": "manchester"})

    assert places.status_code == 200
    assert any(item["id"] == "manchester" for item in places.json())
    london = next(item for item in places.json() if item["id"] == "london")
    assert any(area["id"] == "croydon" and area["grid_region"] == "South East England" for area in london["areas"])
    body = overview.json()
    assert overview.status_code == 200
    assert body["location"]["scope"] == "regional"
    assert body["location"]["gsp_region"] == "G"
    assert body["current"]["forecast"] == 2
    assert body["generation"]["mix"][0]["fuel"] == "wind"


@pytest.mark.asyncio
async def test_overview_area_uses_district_postcode() -> None:
    app = build_test_app()
    seen: list[str] = []
    original = app.state.carbon_client.get_regional_by_postcode

    async def track(postcode: str):
        seen.append(postcode)
        return await original(postcode)

    app.state.carbon_client.get_regional_by_postcode = track
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        overview = await client.get("/v1/overview", params={"city": "london", "area": "croydon"})

    assert overview.status_code == 200
    body = overview.json()
    assert seen[0] == "CR0"
    assert body["location"]["city_id"] == "london"
    assert body["location"]["area_id"] == "croydon"
    assert body["location"]["label"] == "London · Croydon"
    assert "South East" in (body["location"]["grid_note"] or "")
    assert "Kingston" in body["location"]["shared_with"]


@pytest.mark.asyncio
async def test_overview_empty_regional_payload_is_not_500() -> None:
    app = build_test_app()

    async def empty_regional(postcode: str):
        from app.schemas.carbon import RegionalLocationResponse

        return RegionalLocationResponse.model_validate({"data": []})

    app.state.carbon_client.get_regional_by_postcode = empty_regional
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        overview = await client.get("/v1/overview", params={"city": "manchester"})

    assert overview.status_code == 404
    assert "No NESO regional carbon data" in overview.json()["detail"]


@pytest.mark.asyncio
async def test_carbon_history_live_fallback_honors_hours_and_region() -> None:
    from datetime import timedelta

    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        national = await client.get("/v1/carbon/history", params={"hours": 6, "region": "GB"})
        regional = await client.get("/v1/carbon/history", params={"hours": 12, "region": "3"})
        invalid = await client.get("/v1/carbon/history", params={"region": "northwest"})

    assert national.status_code == 200
    start, end = app.state.carbon_client.last_intensity_range
    assert end - start == timedelta(hours=6)
    assert regional.status_code == 200
    start, end, region_id = app.state.carbon_client.last_regional_range
    assert region_id == 3
    assert end - start == timedelta(hours=12)
    assert invalid.status_code == 400


@pytest.mark.asyncio
async def test_price_history_live_fallback_honors_hours() -> None:
    from datetime import timedelta

    app = build_test_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/prices/history", params={"hours": 48})

    assert response.status_code == 200
    period_from, period_to = app.state.octopus_client.last_rate_window
    assert period_to - period_from == timedelta(hours=96)
