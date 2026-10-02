"""Snapshot worker process."""

from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.http import HttpClient
from app.clients.octopus import OctopusEnergyClient
from app.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import create_engine, create_session_factory
from app.jobs.retrain import run_retrain_job
from app.jobs.snapshot import run_snapshot_loop

logger = get_logger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    carbon_http = HttpClient(base_url=str(settings.carbon_intensity_base_url))
    octopus_http = HttpClient(base_url=str(settings.octopus_base_url))
    redis = Redis.from_url(str(settings.redis_url), decode_responses=True, socket_connect_timeout=0.5)
    try:
        await redis.ping()
    except Exception:
        logger.warning("redis_unavailable_worker_continues")
    finally:
        await redis.aclose()

    logger.info("snapshot_worker_started", extra={"interval": settings.snapshot_interval_seconds})
    try:
        async with session_factory() as session:
            await run_retrain_job(session=session)
        await run_snapshot_loop(
            session_factory=session_factory,
            carbon_client=CarbonIntensityClient(carbon_http),
            octopus_client=OctopusEnergyClient(octopus_http),
            settings=settings,
        )
    finally:
        await carbon_http.aclose()
        await octopus_http.aclose()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
