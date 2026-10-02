from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.config import Settings, get_settings
from app.core.errors import utcnow
from app.schemas.api import HealthCheck, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/v1/health", response_model=HealthResponse, include_in_schema=False)
async def health(request: Request) -> HealthResponse:
    settings: Settings = get_settings()
    db_status: str = "error"
    redis_status: str = "error"

    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        db_status = "skipped"
    else:
        try:
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "error"

    cache = getattr(request.app.state, "cache", None)
    if cache is None:
        redis_status = "skipped"
    else:
        try:
            await cache.ping()
            redis_status = "ok"
        except Exception:
            redis_status = "error"

    overall = "ok" if db_status in {"ok", "skipped"} and redis_status in {"ok", "skipped"} else "degraded"
    if db_status == "error" or redis_status == "error":
        overall = "degraded"

    return HealthResponse(
        status=overall,  # type: ignore[arg-type]
        version=settings.app_version,
        checks=HealthCheck(database=db_status, redis=redis_status),  # type: ignore[arg-type]
        timestamp=utcnow(),
    )
