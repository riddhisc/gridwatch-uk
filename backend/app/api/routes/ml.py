from fastapi import APIRouter, Request

from app.ml.inference import get_daily_summary, get_forecast, get_recommendations, predict_next_hour
from app.schemas.api import MLForecastResponse, MLUnavailableResponse

router = APIRouter(prefix="/v1", tags=["ml"])


@router.get("/recommendations", response_model=MLUnavailableResponse)
async def recommendations() -> MLUnavailableResponse:
    return get_recommendations()


@router.get("/forecast", response_model=MLUnavailableResponse)
async def forecast() -> MLUnavailableResponse:
    return get_forecast()


@router.get("/forecast/ml", response_model=MLForecastResponse)
async def ml_forecast(request: Request) -> MLForecastResponse:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        return MLForecastResponse(
            available=False,
            reason="database_unavailable",
            message="No database session is configured.",
        )
    async with session_factory() as session:
        return await predict_next_hour(session)


@router.get("/summary", response_model=MLUnavailableResponse)
async def summary() -> MLUnavailableResponse:
    return get_daily_summary()
