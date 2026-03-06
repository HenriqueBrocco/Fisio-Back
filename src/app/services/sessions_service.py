from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session as SessionModel
from app.models.session import SessionSummary as SessionSummaryModel
from app.models.user import User


class SessionAccessError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


def ensure_session_access(user: User, sess: SessionModel) -> None:
    if user.role == "PATIENT" and sess.patient_user_id != user.id:
        raise SessionAccessError("Sem permissão para esta sessão.")


def get_session(db: DBSession, session_id: str) -> SessionModel:
    s = db.execute(select(SessionModel).where(SessionModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise SessionNotFoundError("Sessão não encontrada.")
    return s


def start_session(db: DBSession, user: User, session_id: str) -> SessionModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    if s.status == "CREATED":
        s.status = "RUNNING"
        s.started_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def finish_session(db: DBSession, user: User, session_id: str) -> SessionModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finished_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def upsert_summary(
    db: DBSession,
    user: User,
    session_id: str,
    reps: int,
    rom: float,
    cadence: float | None,
    alerts: list,
) -> SessionSummaryModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    summary = db.execute(
        select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
    ).scalar_one_or_none()

    if summary:
        summary.reps = reps
        summary.rom = rom
        summary.cadence = cadence
        summary.alerts = alerts
    else:
        summary = SessionSummaryModel(
            session_id=session_id,
            reps=reps,
            rom=rom,
            cadence=cadence,
            alerts=alerts,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary


def get_summary(db: DBSession, user: User, session_id: str) -> SessionSummaryModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    summary = db.execute(
        select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
    ).scalar_one_or_none()
    if not summary:
        raise SessionNotFoundError("Resumo não encontrado.")
    return summary


def finalize_session(
    db: DBSession,
    user: User,
    session_id: str,
    reps: int | None,
    rom: float | None,
    cadence: float | None,
    alerts: list | None,
) -> SessionModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    has_any = any(v is not None for v in [reps, rom, cadence, alerts])
    if has_any:
        summary = db.execute(
            select(SessionSummaryModel).where(SessionSummaryModel.session_id == session_id)
        ).scalar_one_or_none()
        if not summary:
            summary = SessionSummaryModel(
                session_id=session_id, reps=0, rom=0.0, cadence=None, alerts=[]
            )
            db.add(summary)

        if reps is not None:
            summary.reps = reps
        if rom is not None:
            summary.rom = rom
        if cadence is not None:
            summary.cadence = cadence
        if alerts is not None:
            summary.alerts = alerts

    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finished_at = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s
