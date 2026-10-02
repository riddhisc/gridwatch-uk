from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api import api_router
from app.cache.redis import CacheClient
from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.http import HttpClient
from app.clients.octopus import OctopusEnergyClient
from app.config import get_settings
from app.core.logging import configure_logging
from app.db.session import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    redis = Redis.from_url(
        str(settings.redis_url),
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )
    cache = CacheClient(redis)

    carbon_http = HttpClient(
        base_url=str(settings.carbon_intensity_base_url),
        timeout_seconds=settings.http_timeout_seconds,
        retry_attempts=settings.http_retry_attempts,
    )
    octopus_http = HttpClient(
        base_url=str(settings.octopus_base_url),
        timeout_seconds=settings.http_timeout_seconds,
        retry_attempts=settings.http_retry_attempts,
    )

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.cache = cache
    app.state.carbon_client = CarbonIntensityClient(carbon_http)
    app.state.octopus_client = OctopusEnergyClient(octopus_http)
    app.state.carbon_http = carbon_http
    app.state.octopus_http = octopus_http

    try:
        yield
    finally:
        await carbon_http.aclose()
        await octopus_http.aclose()
        await cache.aclose()
        await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Green Power Hours API",
        description=(
            "UK carbon intensity and Octopus Agile pricing so people know when electricity is greener and cheaper."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
