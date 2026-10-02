from __future__ import annotations

from app.core.logging import get_logger
from app.ml.training.train_forecast import InsufficientHistoryError, train_from_database

logger = get_logger(__name__)


async def run_retrain_job(*, session) -> dict | None:
    try:
        meta = await train_from_database(session=session)
        logger.info("ml_retrain_complete", extra={"mae": meta.get("mae"), "rows": meta.get("rows")})
        return meta
    except InsufficientHistoryError as exc:
        logger.warning("ml_retrain_skipped", extra={"reason": str(exc)})
        return None
