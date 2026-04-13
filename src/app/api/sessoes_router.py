from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.sessao import (
    SessaoFinalizadaIn,
    SessaoOut,
    ResumoSessaoIn,
    ResumoSessaoOut,
)
from app.services.sessoes_service import (
    SessionAccessError,
    SessionNotFoundError,
    finalize_session as svc_finalize_session,
    finish_session as svc_finish_session,
    get_session as svc_get_session,
    get_summary as svc_get_summary,
    start_session as svc_start_session,
    upsert_summary as svc_upsert_summary,
)

sessoes_router = APIRouter(prefix="/sessoes", tags=["Sessões"])


@sessoes_router.get("/{session_id}", response_model=SessaoOut)
def get_session(session_id: str, db: DBSession = Depends(get_db), user: Usuario = Depends(get_usuario_atual),):
    try:
        sess = svc_get_session(db, session_id)
        # valida permissão (mantendo o get_session do service "puro")
        if user.perfil == "PATIENT" and sess.paciente_usuario_id != user.id:
            raise SessionAccessError("Sem permissão para esta sessão.")
        return sess
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@sessoes_router.post("/{session_id}/start", response_model=SessaoOut)
def start_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return svc_start_session(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@sessoes_router.post("/{session_id}/finish", response_model=SessaoOut)
def finish_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return svc_finish_session(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@sessoes_router.post("/{session_id}/summary", response_model=ResumoSessaoOut, status_code=status.HTTP_201_CREATED,)
def upsert_session_summary(
    session_id: str,
    payload: ResumoSessaoIn,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return svc_upsert_summary(
            db=db,
            user=user,
            session_id=session_id,
            reps=payload.repeticoes,
            rom=payload.adm,
            cadence=payload.cadencia,
            alerts=payload.alertas,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@sessoes_router.get("/{session_id}/summary", response_model=ResumoSessaoOut)
def get_session_summary(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return svc_get_summary(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@sessoes_router.post("/{session_id}/finalize", response_model=SessaoOut)
def finalize_session(
    session_id: str,
    payload: SessaoFinalizadaIn,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return svc_finalize_session(
            db=db,
            user=user,
            session_id=session_id,
            reps=payload.repeticoes,
            rom=payload.adm,
            cadence=payload.cadencia,
            alerts=payload.alertas,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
