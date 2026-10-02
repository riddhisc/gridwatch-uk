from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class IntensityValues(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    forecast: int | None = None
    actual: int | None = None
    index: str | None = None


class IntensityPeriod(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    from_: datetime = Field(alias="from")
    to: datetime
    intensity: IntensityValues


class IntensityResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[IntensityPeriod]

    @model_validator(mode="before")
    @classmethod
    def _normalize_data(cls, value: Any) -> Any:
        if isinstance(value, dict) and "data" in value:
            return {**value, "data": _as_list(value["data"])}
        return value


class GenerationFuelShare(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fuel: str
    perc: float


class GenerationPeriod(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    from_: datetime = Field(alias="from")
    to: datetime
    generationmix: list[GenerationFuelShare]


class GenerationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[GenerationPeriod]

    @model_validator(mode="before")
    @classmethod
    def _normalize_data(cls, value: Any) -> Any:
        if isinstance(value, dict) and "data" in value:
            return {**value, "data": _as_list(value["data"])}
        return value


class RegionalIntensityBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    regionid: int
    dnoregion: str | None = None
    shortname: str | None = None
    postcode: str | None = None
    intensity: IntensityValues
    generationmix: list[GenerationFuelShare] = Field(default_factory=list)


class RegionalPeriod(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    from_: datetime = Field(alias="from")
    to: datetime
    intensity: IntensityValues | None = None
    generationmix: list[GenerationFuelShare] = Field(default_factory=list)
    regions: list[RegionalIntensityBlock] = Field(default_factory=list)


class RegionalResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[RegionalPeriod]

    @model_validator(mode="before")
    @classmethod
    def _normalize_data(cls, value: Any) -> Any:
        if isinstance(value, dict) and "data" in value:
            return {**value, "data": _as_list(value["data"])}
        return value


class RegionalLocationPeriod(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    from_: datetime = Field(alias="from")
    to: datetime
    intensity: IntensityValues
    generationmix: list[GenerationFuelShare] = Field(default_factory=list)


class RegionalLocationBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")

    regionid: int
    dnoregion: str | None = None
    shortname: str | None = None
    postcode: str | None = None
    data: list[RegionalLocationPeriod]


class RegionalLocationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[RegionalLocationBlock]

    @model_validator(mode="before")
    @classmethod
    def _normalize_data(cls, value: Any) -> Any:
        if isinstance(value, dict) and "data" in value:
            return {**value, "data": _as_list(value["data"])}
        return value


class IntensityFactors(BaseModel):
    model_config = ConfigDict(extra="ignore")

    Biomass: float | None = None
    Coal: float | None = None
    Dutch_Imports: float | None = Field(default=None, alias="Dutch Imports")
    French_Imports: float | None = Field(default=None, alias="French Imports")
    Gas_Combined_Cycle: float | None = Field(default=None, alias="Gas (Combined Cycle)")
    Gas_Open_Cycle: float | None = Field(default=None, alias="Gas (Open Cycle)")
    Hydro: float | None = None
    Irish_Imports: float | None = Field(default=None, alias="Irish Imports")
    Nuclear: float | None = None
    Oil: float | None = None
    Other: float | None = None
    Pumped_Storage: float | None = Field(default=None, alias="Pumped Storage")
    Solar: float | None = None
    Wind: float | None = None


class FactorsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[dict[str, Any]] | IntensityFactors | None = None
