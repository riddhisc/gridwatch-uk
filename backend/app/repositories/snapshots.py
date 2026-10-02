from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import utcnow
from app.db.models import CarbonSnapshot, PriceSnapshot


class SnapshotRepository:
    async def upsert_carbon(self, session: AsyncSession, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        stmt = pg_insert(CarbonSnapshot).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_carbon_period_region",
            set_={
                "forecast_intensity": stmt.excluded.forecast_intensity,
                "actual_intensity": stmt.excluded.actual_intensity,
                "intensity_index": stmt.excluded.intensity_index,
                "region_name": stmt.excluded.region_name,
                "fetched_at": stmt.excluded.fetched_at,
            },
        )
        await session.execute(stmt)
        return len(rows)

    async def update_generation_mix(self, session: AsyncSession, updates: list[dict[str, Any]]) -> int:
        count = 0
        for item in updates:
            result = await session.execute(
                update(CarbonSnapshot)
                .where(
                    CarbonSnapshot.period_from == item["period_from"],
                    CarbonSnapshot.period_to == item["period_to"],
                    CarbonSnapshot.region_code == item["region_code"],
                )
                .values(generation_mix=item["generation_mix"], fetched_at=utcnow())
            )
            count += result.rowcount or 0
        return count

    async def upsert_prices(self, session: AsyncSession, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        stmt = pg_insert(PriceSnapshot).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_price_period_tariff",
            set_={
                "product_code": stmt.excluded.product_code,
                "gsp_region": stmt.excluded.gsp_region,
                "value_exc_vat": stmt.excluded.value_exc_vat,
                "value_inc_vat": stmt.excluded.value_inc_vat,
                "fetched_at": stmt.excluded.fetched_at,
            },
        )
        await session.execute(stmt)
        return len(rows)

    async def list_carbon(
        self,
        session: AsyncSession,
        *,
        region_code: str,
        start: datetime,
        end: datetime,
    ) -> list[CarbonSnapshot]:
        result = await session.execute(
            select(CarbonSnapshot)
            .where(
                CarbonSnapshot.region_code == region_code,
                CarbonSnapshot.period_from >= start,
                CarbonSnapshot.period_from < end,
            )
            .order_by(CarbonSnapshot.period_from.asc())
        )
        return list(result.scalars().all())

    async def list_prices(
        self,
        session: AsyncSession,
        *,
        tariff_code: str | None,
        start: datetime,
        end: datetime,
    ) -> list[PriceSnapshot]:
        stmt = select(PriceSnapshot).where(
            PriceSnapshot.period_from >= start,
            PriceSnapshot.period_from < end,
        )
        if tariff_code:
            stmt = stmt.where(PriceSnapshot.tariff_code == tariff_code)
        stmt = stmt.order_by(PriceSnapshot.period_from.asc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_carbon_history(
        self,
        session: AsyncSession,
        *,
        region_code: str = "GB",
    ) -> list[CarbonSnapshot]:
        result = await session.execute(
            select(CarbonSnapshot)
            .where(CarbonSnapshot.region_code == region_code)
            .order_by(CarbonSnapshot.period_from.asc())
        )
        return list(result.scalars().all())
