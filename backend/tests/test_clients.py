from datetime import UTC, datetime

import httpx
import pytest
import respx

from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.http import HttpClient
from app.clients.octopus import OctopusEnergyClient
from app.core.errors import UpstreamAPIError


@pytest.mark.asyncio
@respx.mock
async def test_current_intensity_parses_live_shape() -> None:
    respx.get("https://api.carbonintensity.org.uk/intensity").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "from": "2026-09-19T08:00Z",
                        "to": "2026-09-19T08:30Z",
                        "intensity": {"forecast": 120, "actual": 118, "index": "low"},
                    }
                ]
            },
        )
    )
    http = HttpClient(base_url="https://api.carbonintensity.org.uk", retry_attempts=2, timeout_seconds=5)
    client = CarbonIntensityClient(http)
    result = await client.get_current_intensity()
    period = result.data[0]
    assert period.intensity.actual == 118
    assert period.from_ == datetime(2026, 9, 19, 8, 0, tzinfo=UTC)
    await http.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_retries_then_raises_on_persistent_500() -> None:
    respx.get("https://api.carbonintensity.org.uk/intensity").mock(return_value=httpx.Response(500, text="boom"))
    http = HttpClient(base_url="https://api.carbonintensity.org.uk", retry_attempts=2, timeout_seconds=5)
    client = CarbonIntensityClient(http)
    with pytest.raises(UpstreamAPIError):
        await client.get_current_intensity()
    await http.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_octopus_unit_rates_parse() -> None:
    respx.get("https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-C/standard-unit-rates/").mock(
        return_value=httpx.Response(
            200,
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "value_exc_vat": 10.0,
                        "value_inc_vat": 10.5,
                        "valid_from": "2026-09-19T00:00:00Z",
                        "valid_to": "2026-09-19T00:30:00Z",
                    }
                ],
            },
        )
    )
    http = HttpClient(base_url="https://api.octopus.energy/v1", retry_attempts=1, timeout_seconds=5)
    client = OctopusEnergyClient(http)
    rates = await client.get_standard_unit_rates(
        product_code="AGILE-24-10-01",
        tariff_code="E-1R-AGILE-24-10-01-C",
    )
    assert rates[0].value_inc_vat == 10.5
    assert client.tariff_code_for("AGILE-24-10-01", "c") == "E-1R-AGILE-24-10-01-C"
    await http.aclose()
