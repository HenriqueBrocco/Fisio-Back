from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual, exigir_permissao
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.sessao import SessaoCreate, SessaoOut
from app.services.sessoes_paciente_service import (
    BadRequestError,
    NotFoundError,
    create_session_for_patient,
    list_sessions_for_patient,
)

sessoes_paciente_router = APIRouter(prefix="/pacientes", tags=["Sessões do Paciente"])


@sessoes_paciente_router.post(
    "/{patient_id}/sessions", response_model=SessaoOut, status_code=status.HTTP_201_CREATED
)
def create_patient_session(
    patient_id: str,
    payload: SessaoCreate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return create_session_for_patient(
            db=db,
            patient_id=patient_id,
            exercise_id=payload.exercicio_id,
            assignment_id=payload.prescricao_id,
            config_snapshot=payload.config_snapshot,
            pro_user=user,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@sessoes_paciente_router.get("/{patient_id}/sessions", response_model=list[SessaoOut])
def list_patient_sessions(
    patient_id: str,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return list_sessions_for_patient(db, user, patient_id)
    except BadRequestError as e:
        # permissão
        if str(e) == "Sem permissão":
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
