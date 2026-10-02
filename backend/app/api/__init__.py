from fastapi import APIRouter

from app.api.routes.carbon import router as carbon_router
from app.api.routes.health import router as health_router
from app.api.routes.locations import router as locations_router
from app.api.routes.ml import router as ml_router
from app.api.routes.overview import router as overview_router
from app.api.routes.prices import router as prices_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(carbon_router)
api_router.include_router(prices_router)
api_router.include_router(locations_router)
api_router.include_router(overview_router)
api_router.include_router(ml_router)
