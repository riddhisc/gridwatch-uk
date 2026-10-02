from __future__ import annotations

from datetime import datetime

from app.clients.http import HttpClient
from app.core.errors import format_octopus_datetime
from app.schemas.octopus import (
    PaginatedGridSupplyPoints,
    PaginatedProducts,
    PaginatedUnitRates,
    ProductSummary,
    UnitRate,
)


class OctopusEnergyClient:

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list_products(self, *, page: int = 1) -> PaginatedProducts:
        payload = await self._http.get_json(
            "/products/",
            params={
                "brand": "OCTOPUS_ENERGY",
                "is_business": "false",
                "is_prepay": "false",
                "page": page,
            },
        )
        return PaginatedProducts.model_validate(payload)

    async def discover_current_agile_product(self) -> ProductSummary | None:
        page = 1
        while page <= 8:
            listing = await self.list_products(page=page)
            for product in listing.results:
                code = product.code.upper()
                name = (product.display_name or product.full_name or "").lower()
                if product.available_to is not None:
                    continue
                if code.startswith("AGILE") or "agile" in name:
                    return product
            if not listing.next:
                break
            page += 1
        return None

    def tariff_code_for(self, product_code: str, gsp_region: str) -> str:
        region = gsp_region.strip().upper().replace("_", "")
        if len(region) != 1:
            raise ValueError("GSP region must be a single letter, e.g. C for London")
        return f"E-1R-{product_code}-{region}"

    @staticmethod
    def gsp_letter(group_id: str) -> str:
        return group_id.strip().upper().replace("_", "")[-1]

    async def get_grid_supply_point(self, postcode: str) -> str | None:
        compact = "".join(postcode.split()).upper()
        payload = await self._http.get_json(
            "/industry/grid-supply-points/",
            params={"postcode": compact},
        )
        listing = PaginatedGridSupplyPoints.model_validate(payload)
        if not listing.results:
            return None
        return self.gsp_letter(listing.results[0].group_id)

    async def get_standard_unit_rates(
        self,
        *,
        product_code: str,
        tariff_code: str,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int = 1500,
    ) -> list[UnitRate]:
        params: dict[str, str | int] = {"page_size": min(page_size, 1500)}
        if period_from is not None:
            params["period_from"] = format_octopus_datetime(period_from)
        if period_to is not None:
            params["period_to"] = format_octopus_datetime(period_to)

        path: str | None = f"/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
        rates: list[UnitRate] = []
        request_params: dict[str, str | int] | None = params

        while path:
            payload = await self._http.get_json(path, params=request_params)
            page = PaginatedUnitRates.model_validate(payload)
            rates.extend(page.results)
            path = str(page.next) if page.next else None
            request_params = None

        return rates
