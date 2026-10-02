from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from app.db.models import CarbonSnapshot
from app.ml.features import snapshots_to_frame, training_table
from app.ml.inference import unavailable
from app.ml.training.train_forecast import InsufficientHistoryError, train_from_frame


def _synthetic_snapshots(hours: int = 80) -> list[CarbonSnapshot]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = []
    for i in range(hours * 2):
        t = start + timedelta(minutes=30 * i)
        value = 80 + 40 * ((i % 48) / 48) + (5 if i % 48 > 32 else 0)
        rows.append(
            CarbonSnapshot(
                period_from=t,
                period_to=t + timedelta(minutes=30),
                region_code="GB",
                actual_intensity=int(value),
                forecast_intensity=int(value),
            )
        )
    return rows


def test_training_pipeline_runs_on_synthetic_history(tmp_path, monkeypatch) -> None:
    from app.ml.training import train_forecast as module

    monkeypatch.setattr(module, "MODELS_DIR", tmp_path)
    frame = snapshots_to_frame(_synthetic_snapshots(80))
    meta = train_from_frame(frame, min_rows=50)
    assert meta["mae"] >= 0
    assert meta["naive_mae"] >= 0
    assert "model_version" in meta
    assert list(tmp_path.glob("forecast_gb_*.joblib"))


def test_training_refuses_tiny_history() -> None:
    frame = snapshots_to_frame(_synthetic_snapshots(10))
    with pytest.raises(InsufficientHistoryError, match="usable half-hour"):
        train_from_frame(frame, min_rows=96)


def test_inference_fallback_when_no_model(monkeypatch, tmp_path) -> None:
    from app.ml import inference as module

    monkeypatch.setattr(module, "MODELS_DIR", tmp_path)
    response = unavailable("model_not_yet_trained", "No trained model file exists yet.")
    assert response.available is False
    assert response.reason == "model_not_yet_trained"
    assert module._latest_model_files() is None


def test_feature_table_has_expected_columns() -> None:
    table = training_table(snapshots_to_frame(_synthetic_snapshots(40)))
    assert "lag_1" in table.columns
    assert "target" in table.columns
    assert not table.empty
    assert isinstance(table["period_from"].iloc[0], pd.Timestamp | datetime)
