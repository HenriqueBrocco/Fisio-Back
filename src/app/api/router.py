from fastapi import APIRouter

from app.api.prescricoes_router import prescricoes_router
from app.api.auth_router import auth_router
from app.api.exercicios_router import exercicios_router
from app.api.healthcheck_router import healthcheck_router
from app.api.infer_ws import router as infer_ws_router
from app.api.me_router import me_router
from app.api.my_router import my_router
from app.api.sessoes_paciente_router import sessoes_paciente_router
from app.api.pacientes_router import pacientes_router
from app.api.sessoes_router import sessoes_router

api_router = APIRouter()

api_router.include_router(healthcheck_router)
api_router.include_router(auth_router)
api_router.include_router(pacientes_router)
api_router.include_router(sessoes_paciente_router)
api_router.include_router(exercicios_router)
api_router.include_router(prescricoes_router)
api_router.include_router(sessoes_router)
api_router.include_router(infer_ws_router)
api_router.include_router(me_router)
api_router.include_router(my_router)
# api_router.include_router(infer_router)
