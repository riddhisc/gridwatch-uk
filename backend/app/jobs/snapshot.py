from __future__ import annotations

import asyncio
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.octopus import OctopusEnergyClient
from app.config import Settings
from app.core.errors import utcnow
from app.core.logging import get_logger
from app.jobs.retrain import run_retrain_job
from app.repositories.snapshots import SnapshotRepository
from app.services.snapshot_builder import generation_mix_updates, intensity_rows, price_rows

logger = get_logger(__name__)
repo = SnapshotRepository()


def _stamp(rows: list[dict]) -> list[dict]:
    fetched = utcnow()
    for row in rows:
        row["fetched_at"] = fetched
    return rows


async def run_snapshot_job(
    *,
    session: AsyncSession,
    carbon_client: CarbonIntensityClient,
    octopus_client: OctopusEnergyClient,
    settings: Settings,
) -> dict[str, int]:
    now = utcnow()
    intensity_past = await carbon_client.get_past_24h(now)
    intensity_ahead = await carbon_client.get_forecast_48h(now)
    carbon_count = await repo.upsert_carbon(
        session,
        _stamp(intensity_rows(intensity_past.data + intensity_ahead.data)),
    )

    mix_count = 0
    try:
        generation = await carbon_client.get_generation_range(now - timedelta(hours=24), now)
        mix_count = await repo.update_generation_mix(session, generation_mix_updates(generation.data))
    except Exception:
        logger.warning("generation_range_failed", exc_info=True)
        current_mix = await carbon_client.get_generation_mix()
        mix_count = await repo.update_generation_mix(session, generation_mix_updates(current_mix.data))

    product_code = settings.octopus_default_product_code.strip()
    if not product_code:
        product = await octopus_client.discover_current_agile_product()
        product_code = product.code if product else ""
    price_count = 0
    if product_code:
        tariff = octopus_client.tariff_code_for(product_code, settings.octopus_default_gsp_region)
        rates = await octopus_client.get_standard_unit_rates(
            product_code=product_code,
            tariff_code=tariff,
            period_from=now - timedelta(hours=12),
            period_to=now + timedelta(hours=24),
        )
        price_count = await repo.upsert_prices(
            session,
            _stamp(
                price_rows(
                    rates,
                    product_code=product_code,
                    tariff_code=tariff,
                    gsp_region=settings.octopus_default_gsp_region,
                )
            ),
        )

    await session.commit()
    summary = {
        "carbon_periods": carbon_count,
        "generation_updates": mix_count,
        "price_periods": price_count,
    }
    logger.info("snapshot_job_complete", extra=summary)
    return summary


async def run_snapshot_loop(
    *,
    session_factory: async_sessionmaker[AsyncSession],
    carbon_client: CarbonIntensityClient,
    octopus_client: OctopusEnergyClient,
    settings: Settings,
) -> None:
    interval = settings.snapshot_interval_seconds
    retrain_every = max(settings.retrain_interval_seconds, interval)
    elapsed = retrain_every
    while True:
        try:
            async with session_factory() as session:
                await run_snapshot_job(
                    session=session,
                    carbon_client=carbon_client,
                    octopus_client=octopus_client,
                    settings=settings,
                )
                if elapsed >= retrain_every:
                    await run_retrain_job(session=session)
                    elapsed = 0
        except Exception:
            logger.exception("snapshot_job_failed")
        await asyncio.sleep(interval)
        elapsed += interval
