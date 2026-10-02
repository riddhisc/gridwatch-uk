from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CarbonSnapshot(Base):
    __tablename__ = "carbon_snapshots"
    __table_args__ = (
        UniqueConstraint("period_from", "period_to", "region_code", name="uq_carbon_period_region"),
        Index("ix_carbon_snapshots_period_from", "period_from"),
        Index("ix_carbon_snapshots_region_period", "region_code", "period_from"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    period_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    region_code: Mapped[str] = mapped_column(String(32), nullable=False, default="GB")
    region_name: Mapped[str | None] = mapped_column(String(128))
    forecast_intensity: Mapped[int | None]
    actual_intensity: Mapped[int | None]
    intensity_index: Mapped[str | None] = mapped_column(String(32))
    generation_mix: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(String(64), default="neso_carbon_intensity")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (
        UniqueConstraint("period_from", "period_to", "tariff_code", name="uq_price_period_tariff"),
        Index("ix_price_snapshots_period_from", "period_from"),
        Index("ix_price_snapshots_tariff_period", "tariff_code", "period_from"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    period_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    product_code: Mapped[str] = mapped_column(String(64), nullable=False)
    tariff_code: Mapped[str] = mapped_column(String(128), nullable=False)
    gsp_region: Mapped[str] = mapped_column(String(8), nullable=False)
    value_exc_vat: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    value_inc_vat: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="octopus_agile")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
