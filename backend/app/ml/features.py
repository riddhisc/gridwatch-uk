"""Forecast feature helpers."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.db.models import CarbonSnapshot

FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "lag_1",
    "lag_2",
    "lag_48",
    "roll_mean_4",
    "roll_mean_48",
]

HORIZON_STEPS = 2  # 1 hour ahead at 30-minute intervals


def intensity_value(row: CarbonSnapshot) -> float | None:
    if row.actual_intensity is not None:
        return float(row.actual_intensity)
    if row.forecast_intensity is not None:
        return float(row.forecast_intensity)
    return None


def snapshots_to_frame(rows: list[CarbonSnapshot]) -> pd.DataFrame:
    records = []
    for row in rows:
        value = intensity_value(row)
        if value is None:
            continue
        records.append({"period_from": row.period_from, "intensity": value})
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        return frame
    frame = frame.sort_values("period_from").drop_duplicates("period_from").reset_index(drop=True)
    return frame


def add_forecast_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["hour"] = out["period_from"].dt.hour
    out["day_of_week"] = out["period_from"].dt.dayofweek
    out["lag_1"] = out["intensity"].shift(1)
    out["lag_2"] = out["intensity"].shift(2)
    out["lag_48"] = out["intensity"].shift(48).fillna(out["intensity"].shift(1))
    out["roll_mean_4"] = out["intensity"].shift(1).rolling(4, min_periods=4).mean()
    out["roll_mean_48"] = out["intensity"].shift(1).rolling(48, min_periods=12).mean()
    out["target"] = out["intensity"].shift(-HORIZON_STEPS)
    out["target_time"] = out["period_from"].shift(-HORIZON_STEPS)
    return out


def training_table(frame: pd.DataFrame) -> pd.DataFrame:
    featured = add_forecast_features(frame)
    return featured.dropna(subset=[*FEATURE_COLUMNS, "target"]).reset_index(drop=True)


def inference_row(frame: pd.DataFrame) -> tuple[pd.DataFrame, datetime] | None:
    featured = add_forecast_features(frame)
    usable = featured.dropna(subset=FEATURE_COLUMNS)
    if usable.empty:
        return None
    last = usable.iloc[[-1]]
    predicted_for = last["period_from"].iloc[0] + pd.Timedelta(minutes=30 * HORIZON_STEPS)
    return last[FEATURE_COLUMNS], predicted_for.to_pydatetime()
