from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.patients import router as patients_router
from app.api.sessions import router as sessions_router
from app.api.exercises import router as exercises_router
from app.api.infer_ws import router as infer_router
from app.api.auth import router as auth_router
from app.api.me import router as me_router
from app.api.patient_sessions import router as patient_sessions_router
from app.api.assignments import router as assignments_router
from app.api.infer_ws import router as infer_ws_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(patients_router)
api_router.include_router(sessions_router)
api_router.include_router(exercises_router)
api_router.include_router(infer_router)
api_router.include_router(auth_router)
api_router.include_router(me_router)
api_router.include_router(patient_sessions_router)
api_router.include_router(assignments_router)
api_router.include_router(infer_ws_router)