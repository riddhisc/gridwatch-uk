from functools import lru_cache
from typing import Literal

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+psycopg://gridwatch:gridwatch@localhost:5432/gridwatch"
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    carbon_intensity_base_url: HttpUrl = Field(default="https://api.carbonintensity.org.uk")
    octopus_base_url: HttpUrl = Field(default="https://api.octopus.energy/v1")
    octopus_default_gsp_region: str = "C"
    octopus_default_product_code: str = ""

    cache_ttl_carbon_seconds: int = 60
    cache_ttl_price_seconds: int = 120
    snapshot_interval_seconds: int = 1800
    retrain_interval_seconds: int = 86400
    ml_min_train_rows: int = 96

    http_timeout_seconds: float = 15.0
    http_retry_attempts: int = 3

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("postgresql+psycopg", "postgresql+psycopg")


@lru_cache
def get_settings() -> Settings:
    return Settings()
