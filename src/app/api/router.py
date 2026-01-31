from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.api.sessions import router as sessions_router
#from app.api.exercises import router as exercises_router
from app.api.infer import router as infer_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(patients_router)
api_router.include_router(sessions_router)
#api_router.include_router(exercises_router)
api_router.include_router(infer_router)
