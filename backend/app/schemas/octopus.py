from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UnitRate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    value_exc_vat: float
    value_inc_vat: float
    valid_from: datetime
    valid_to: datetime | None = None
    payment_method: str | None = None


class PaginatedUnitRates(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[UnitRate]


class ProductSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code: str
    direction: str | None = None
    full_name: str | None = None
    display_name: str | None = None
    description: str | None = None
    is_variable: bool | None = None
    is_green: bool | None = None
    is_tracker: bool | None = None
    is_prepay: bool | None = None
    is_business: bool | None = None
    brand: str | None = None
    available_from: datetime | None = None
    available_to: datetime | None = None
    links: list[dict] = Field(default_factory=list)


class PaginatedProducts(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[ProductSummary]


class GridSupplyPoint(BaseModel):
    model_config = ConfigDict(extra="ignore")

    group_id: str
    gsp_id: str | None = None
    gsp_name: str | None = None


class PaginatedGridSupplyPoints(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int | None = None
    next: HttpUrl | None = None
    previous: HttpUrl | None = None
    results: list[GridSupplyPoint]
