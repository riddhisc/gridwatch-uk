"""Train a next-hour carbon intensity model from stored snapshots."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.ml.features import FEATURE_COLUMNS, snapshots_to_frame, training_table

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MIN_TRAIN_ROWS = 96  # ~2 days of half-hours; enough to run, not enough for weekly patterns
RECOMMENDED_DAYS = 14


class InsufficientHistoryError(Exception):
    """Raised when stored snapshots are too few to train a model."""


def _span_days(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0
    delta = frame["period_from"].max() - frame["period_from"].min()
    return float(delta.total_seconds() / 86400)


def train_from_frame(frame: pd.DataFrame, *, min_rows: int = MIN_TRAIN_ROWS) -> dict:
    table = training_table(frame)
    span_days = _span_days(frame)
    if len(table) < min_rows:
        days = span_days
        raise InsufficientHistoryError(
            f"Only {len(table)} usable half-hour rows after feature building "
            f"({days:.1f} days of snapshots). Minimum {min_rows} rows required "
            f"(about {RECOMMENDED_DAYS} days is better for daily/weekly patterns)."
        )

    split = max(int(len(table) * 0.8), 1)
    train_df = table.iloc[:split]
    test_df = table.iloc[split:]
    if test_df.empty:
        test_df = train_df.tail(max(8, len(train_df) // 5))

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target"]
    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df["target"]

    model = GradientBoostingRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        random_state=42,
    )
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    naive = test_df["intensity"].to_numpy(dtype=float)

    mae = float(mean_absolute_error(y_test, predicted))
    rmse = float(np.sqrt(mean_squared_error(y_test, predicted)))
    naive_mae = float(mean_absolute_error(y_test, naive))

    version = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / f"forecast_gb_{version}.joblib"
    meta_path = MODELS_DIR / f"forecast_gb_{version}.json"
    joblib.dump(model, model_path)
    metadata = {
        "model_version": version,
        "model_path": str(model_path),
        "rows": int(len(table)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "span_days": round(span_days, 2),
        "limited_history": span_days < RECOMMENDED_DAYS,
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "naive_mae": round(naive_mae, 3),
        "beats_naive": mae < naive_mae,
        "feature_columns": FEATURE_COLUMNS,
        "saved_at": version,
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


async def train_from_database(*, session, region_code: str = "GB", min_rows: int = MIN_TRAIN_ROWS) -> dict:
    from app.repositories.snapshots import SnapshotRepository

    rows = await SnapshotRepository().list_carbon_history(session, region_code=region_code)
    frame = snapshots_to_frame(rows)
    return train_from_frame(frame, min_rows=min_rows)


def main() -> None:
    import asyncio

    from app.config import get_settings
    from app.db.session import create_engine, create_session_factory

    async def _run() -> None:
        settings = get_settings()
        engine = create_engine(settings)
        factory = create_session_factory(engine)
        try:
            async with factory() as session:
                meta = await train_from_database(session=session)
                print(json.dumps(meta, indent=2))
        finally:
            await engine.dispose()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
