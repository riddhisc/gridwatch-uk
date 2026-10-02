from __future__ import annotations

import json
from pathlib import Path

import joblib
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.features import inference_row, snapshots_to_frame
from app.ml.training.train_forecast import MODELS_DIR
from app.repositories.snapshots import SnapshotRepository
from app.schemas.api import MLForecastResponse, MLUnavailableResponse

repo = SnapshotRepository()


def get_recommendations() -> MLUnavailableResponse:
    return MLUnavailableResponse(
        feature="recommendations",
        message="Recommendations are not available yet.",
    )


def get_forecast() -> MLUnavailableResponse:
    return MLUnavailableResponse(
        feature="forecast",
        message="NESO's 48-hour outlook is at GET /v1/carbon/forecast. Our own model is GET /v1/forecast/ml.",
    )


def get_daily_summary() -> MLUnavailableResponse:
    return MLUnavailableResponse(
        feature="summary",
        message="Daily summaries are not available yet.",
    )


def _latest_model_files() -> tuple[Path, Path] | None:
    if not MODELS_DIR.exists():
        return None
    models = sorted(MODELS_DIR.glob("forecast_gb_*.joblib"))
    if not models:
        return None
    model_path = models[-1]
    meta_path = model_path.with_suffix(".json")
    return model_path, meta_path


def unavailable(reason: str, message: str) -> MLForecastResponse:
    return MLForecastResponse(
        available=False,
        reason=reason,
        message=message,
    )


async def predict_next_hour(session: AsyncSession, *, region_code: str = "GB") -> MLForecastResponse:
    files = _latest_model_files()
    if files is None:
        return unavailable("model_not_yet_trained", "No trained model file exists yet.")
    model_path, meta_path = files
    try:
        model = joblib.load(model_path)
        metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        rows = await repo.list_carbon_history(session, region_code=region_code)
        frame = snapshots_to_frame(rows)
        packed = inference_row(frame)
        if packed is None:
            return unavailable("not_enough_recent_rows", "Not enough recent snapshots to build features.")
        features, predicted_for = packed
        prediction = float(model.predict(features)[0])
        return MLForecastResponse(
            available=True,
            prediction=round(prediction, 1),
            predicted_for=predicted_for,
            model_version=str(metadata.get("model_version", model_path.stem)),
            mae=metadata.get("mae"),
            naive_mae=metadata.get("naive_mae"),
            limited_history=bool(metadata.get("limited_history", True)),
            history_days=metadata.get("span_days"),
            message=(
                "This is our 1-hour guess from stored snapshots, not NESO's official forecast. "
                "History is still short, so treat it as a demo."
                if metadata.get("limited_history")
                else "1-hour carbon guess trained on stored snapshots."
            ),
        )
    except Exception:
        return unavailable("inference_failed", "The model file could not be loaded or used.")
