from __future__ import annotations

from datetime import datetime

from app.clients.http import HttpClient
from app.core.errors import format_ci_datetime
from app.schemas.carbon import (
    FactorsResponse,
    GenerationResponse,
    IntensityResponse,
    RegionalLocationResponse,
    RegionalResponse,
)


class CarbonIntensityClient:

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_current_intensity(self) -> IntensityResponse:
        payload = await self._http.get_json("/intensity")
        return IntensityResponse.model_validate(payload)

    async def get_intensity_for_date(self, date: str) -> IntensityResponse:
        payload = await self._http.get_json(f"/intensity/date/{date}")
        return IntensityResponse.model_validate(payload)

    async def get_intensity_from(self, start: datetime) -> IntensityResponse:
        payload = await self._http.get_json(f"/intensity/{format_ci_datetime(start)}")
        return IntensityResponse.model_validate(payload)

    async def get_intensity_range(self, start: datetime, end: datetime) -> IntensityResponse:
        payload = await self._http.get_json(
            f"/intensity/{format_ci_datetime(start)}/{format_ci_datetime(end)}"
        )
        return IntensityResponse.model_validate(payload)

    async def get_forecast_24h(self, start: datetime) -> IntensityResponse:
        payload = await self._http.get_json(f"/intensity/{format_ci_datetime(start)}/fw24h")
        return IntensityResponse.model_validate(payload)

    async def get_forecast_48h(self, start: datetime) -> IntensityResponse:
        payload = await self._http.get_json(f"/intensity/{format_ci_datetime(start)}/fw48h")
        return IntensityResponse.model_validate(payload)

    async def get_past_24h(self, start: datetime) -> IntensityResponse:
        payload = await self._http.get_json(f"/intensity/{format_ci_datetime(start)}/pt24h")
        return IntensityResponse.model_validate(payload)

    async def get_factors(self) -> FactorsResponse:
        payload = await self._http.get_json("/intensity/factors")
        return FactorsResponse.model_validate(payload)

    async def get_generation_mix(self) -> GenerationResponse:
        payload = await self._http.get_json("/generation")
        return GenerationResponse.model_validate(payload)

    async def get_generation_range(self, start: datetime, end: datetime) -> GenerationResponse:
        payload = await self._http.get_json(
            f"/generation/{format_ci_datetime(start)}/{format_ci_datetime(end)}"
        )
        return GenerationResponse.model_validate(payload)

    async def get_regional_current(self) -> RegionalResponse:
        payload = await self._http.get_json("/regional")
        return RegionalResponse.model_validate(payload)

    async def get_regional_by_postcode(self, postcode: str) -> RegionalLocationResponse:
        outward = postcode.strip().split(" ")[0].upper()
        payload = await self._http.get_json(f"/regional/postcode/{outward}")
        return RegionalLocationResponse.model_validate(payload)

    async def get_regional_by_region_id(self, region_id: int) -> RegionalLocationResponse:
        payload = await self._http.get_json(f"/regional/regionid/{region_id}")
        return RegionalLocationResponse.model_validate(payload)

    async def get_regional_forecast_48h_by_postcode(
        self, start: datetime, postcode: str
    ) -> RegionalLocationResponse:
        outward = postcode.strip().split(" ")[0].upper()
        payload = await self._http.get_json(
            f"/regional/intensity/{format_ci_datetime(start)}/fw48h/postcode/{outward}"
        )
        return RegionalLocationResponse.model_validate(payload)

    async def get_regional_past_24h_by_postcode(
        self, start: datetime, postcode: str
    ) -> RegionalLocationResponse:
        outward = postcode.strip().split(" ")[0].upper()
        payload = await self._http.get_json(
            f"/regional/intensity/{format_ci_datetime(start)}/pt24h/postcode/{outward}"
        )
        return RegionalLocationResponse.model_validate(payload)

    async def get_regional_intensity_range_by_region_id(
        self, start: datetime, end: datetime, region_id: int
    ) -> RegionalLocationResponse:
        payload = await self._http.get_json(
            f"/regional/intensity/{format_ci_datetime(start)}/{format_ci_datetime(end)}/regionid/{region_id}"
        )
        return RegionalLocationResponse.model_validate(payload)
