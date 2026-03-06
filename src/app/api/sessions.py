from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.session import (
    SessionFinalizeIn,
    SessionOut,
    SessionSummaryIn,
    SessionSummaryOut,
)
from app.services.sessions_service import (
    SessionAccessError,
    SessionNotFoundError,
)
from app.services.sessions_service import (
    finalize_session as svc_finalize_session,
)
from app.services.sessions_service import (
    finish_session as svc_finish_session,
)
from app.services.sessions_service import (
    get_session as svc_get_session,
)
from app.services.sessions_service import (
    get_summary as svc_get_summary,
)
from app.services.sessions_service import (
    start_session as svc_start_session,
)
from app.services.sessions_service import (
    upsert_summary as svc_upsert_summary,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        sess = svc_get_session(db, session_id)
        # valida permissão (mantendo o get_session do service "puro")
        if user.role == "PATIENT" and sess.patient_user_id != user.id:
            raise SessionAccessError("Sem permissão para esta sessão.")
        return sess
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{session_id}/start", response_model=SessionOut)
def start_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return svc_start_session(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{session_id}/finish", response_model=SessionOut)
def finish_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return svc_finish_session(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post(
    "/{session_id}/summary",
    response_model=SessionSummaryOut,
    status_code=status.HTTP_201_CREATED,
)
def upsert_session_summary(
    session_id: str,
    payload: SessionSummaryIn,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return svc_upsert_summary(
            db=db,
            user=user,
            session_id=session_id,
            reps=payload.reps,
            rom=payload.rom,
            cadence=payload.cadence,
            alerts=payload.alerts,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{session_id}/summary", response_model=SessionSummaryOut)
def get_session_summary(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return svc_get_summary(db, user, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{session_id}/finalize", response_model=SessionOut)
def finalize_session(
    session_id: str,
    payload: SessionFinalizeIn,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return svc_finalize_session(
            db=db,
            user=user,
            session_id=session_id,
            reps=payload.reps,
            rom=payload.rom,
            cadence=payload.cadence,
            alerts=payload.alerts,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
