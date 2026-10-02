"""Forecasting, recommendations, and summaries."""

from app.ml.inference import (
    get_daily_summary,
    get_forecast,
    get_recommendations,
)

__all__ = ["get_daily_summary", "get_forecast", "get_recommendations"]
