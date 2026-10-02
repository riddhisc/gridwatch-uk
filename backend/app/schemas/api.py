from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.carbon import GenerationFuelShare


class HealthCheck(BaseModel):
    database: Literal["ok", "error", "skipped"]
    redis: Literal["ok", "error", "skipped"]
    carbon_intensity: Literal["ok", "error", "skipped"] = "skipped"


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str = "green-power-hours-api"
    version: str
    checks: HealthCheck
    timestamp: datetime


class CurrentCarbonView(BaseModel):
    period_from: datetime
    period_to: datetime
    forecast: int | None
    actual: int | None
    index: str | None
    region_code: str = "GB"
    region_name: str | None = None
    cached: bool = False


class CurrentGenerationView(BaseModel):
    period_from: datetime
    period_to: datetime
    mix: list[GenerationFuelShare]
    cached: bool = False


class MLUnavailableResponse(BaseModel):
    available: Literal[False] = False
    feature: str
    reason: Literal["not_yet_available", "model_unavailable"] = "not_yet_available"
    message: str = Field(default="This feature is not available yet.")


class MLForecastResponse(BaseModel):
    available: bool
    feature: str = "ml_forecast"
    reason: str | None = None
    message: str | None = None
    prediction: float | None = None
    predicted_for: datetime | None = None
    model_version: str | None = None
    mae: float | None = None
    naive_mae: float | None = None
    history_days: float | None = None
    limited_history: bool = False


class CarbonPoint(BaseModel):
    period_from: datetime
    period_to: datetime
    forecast: int | None = None
    actual: int | None = None
    index: str | None = None
    generation_mix: list[GenerationFuelShare] = Field(default_factory=list)


class PricePoint(BaseModel):
    period_from: datetime
    period_to: datetime
    value_exc_vat: float
    value_inc_vat: float
    product_code: str
    tariff_code: str
    gsp_region: str


class CombinedPoint(BaseModel):
    period_from: datetime
    period_to: datetime
    carbon: int | None = None
    price_inc_vat: float | None = None
    index: str | None = None


class Advice(BaseModel):
    action: Literal["charge_now", "use_now", "wait", "ok"]
    headline: str
    detail: str


class BestWindow(BaseModel):
    period_from: datetime
    period_to: datetime
    carbon: int | None = None
    price_inc_vat: float | None = None
    reason: str


class SnapshotJobResult(BaseModel):
    carbon_periods: int
    generation_updates: int
    price_periods: int


class LocationView(BaseModel):
    id: str
    label: str
    postcode: str | None = None
    neso_region: str | None = None
    neso_region_id: int | None = None
    gsp_region: str | None = None
    gsp_name: str | None = None
    scope: Literal["national", "regional"]
    city_id: str | None = None
    area_id: str | None = None
    shared_with: list[str] = Field(default_factory=list)
    grid_note: str | None = None


class PlaceAreaOption(BaseModel):
    id: str
    name: str
    postcode: str
    grid_region: str | None = None


class PlaceOption(BaseModel):
    id: str
    name: str
    postcode: str
    areas: list[PlaceAreaOption] = Field(default_factory=list)


class OverviewResponse(BaseModel):
    advice: Advice
    location: LocationView
    current: CurrentCarbonView
    generation: CurrentGenerationView
    current_price: PricePoint | None = None
    forecast: list[CarbonPoint]
    history: list[CarbonPoint]
    prices: list[PricePoint]
    combined: list[CombinedPoint]
    best_window: BestWindow | None = None
    recommendations: MLUnavailableResponse
    as_of: datetime
