from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import User
from app.db.session import get_db
from app.models.session import Session as SessionModel, SessionSummary as SessionSummaryModel
from app.schemas.session import (
    SessionOut,
    SessionSummaryIn,
    SessionSummaryOut,
    SessionFinalizeIn
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    _ensure_session_access(user, s)
    return s


@router.post("/{session_id}/summary", response_model=SessionSummaryOut, status_code=status.HTTP_201_CREATED)
def upsert_session_summary(session_id: str, payload: SessionSummaryIn, db: DBSession = Depends(get_db)):
    # garante que a sessão existe
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    summary = db.execute(
        select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
    ).scalar_one_or_none()

    if summary:
        summary.reps = payload.reps
        summary.rom = payload.rom
        summary.cadence = payload.cadence
        summary.alerts = payload.alerts
    else:
        summary = SessionSummaryModel(
            session_id=session_id,
            reps=payload.reps,
            rom=payload.rom,
            cadence=payload.cadence,
            alerts=payload.alerts,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary


@router.get("/{session_id}/summary", response_model=SessionSummaryOut)
def get_session_summary(session_id: str, db: DBSession = Depends(get_db)):
    summary = db.execute(
        select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
    ).scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=404, detail="Resumo não encontrado.")
    return summary

@router.post("/{session_id}/start", response_model=SessionOut)
def start_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    _ensure_session_access(user, s)

    if s.status == "CREATED":
        s.status = "RUNNING"
        s.started_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.post("/{session_id}/finish", response_model=SessionOut)
def finish_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    _ensure_session_access(user, s)

    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finished_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def _ensure_session_access(user: User, sess: SessionModel) -> None:
    if user.role == "PATIENT" and sess.patient_user_id != user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para esta sessão.")
    
@router.post("/{session_id}/finalize", response_model=SessionOut)
def finalize_session(
    session_id: str,
    payload: SessionFinalizeIn,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    _ensure_session_access(user, s)

    # atualiza summary se vier algo no payload
    has_any = any(
        v is not None for v in [payload.reps, payload.rom, payload.cadence, payload.alerts]
    )
    if has_any:
        summary = db.execute(
            select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
        ).scalar_one_or_none()

        if not summary:
            summary = SessionSummaryModel(
                session_id=session_id,
                reps=0,
                rom=0.0,
                cadence=None,
                alerts=[],
            )
            db.add(summary)

        if payload.reps is not None:
            summary.reps = payload.reps
        if payload.rom is not None:
            summary.rom = payload.rom
        if payload.cadence is not None:
            summary.cadence = payload.cadence
        if payload.alerts is not None:
            summary.alerts = payload.alerts

    # finaliza sessão (idempotente)
    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finished_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s