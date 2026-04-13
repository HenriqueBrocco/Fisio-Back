from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.sessao import Sessoes as SessoesModel
from app.models.sessao import ResumoSessao as ResumoSessaoModel
from app.models.usuario import Usuario


class SessionAccessError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


def ensure_session_access(user: Usuario, sess: SessoesModel, db: DBSession) -> None:
    if user.perfil == "PATIENT":
        if sess.paciente_usuario_id != user.id:
            raise SessionAccessError("Sem permissão para esta sessão.")
        return

    # PRO: valida ownership do paciente
    patient = db.execute(select(Usuario).where(Usuario.id == sess.paciente_usuario_id)).scalar_one_or_none()
    if not patient or patient.usuario_pro_id != user.id:
        raise SessionAccessError("Sem permissão para esta sessão.")


def get_session(db: DBSession, session_id: str) -> SessoesModel:
    s = db.execute(select(SessoesModel).where(SessoesModel.id == session_id)).scalar_one_or_none()
    if not s:
        raise SessionNotFoundError("Sessão não encontrada.")
    return s


def start_session(db: DBSession, user: Usuario, session_id: str) -> SessoesModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s, db)

    if s.status == "CREATED":
        s.status = "RUNNING"
        s.iniciado_em = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def finish_session(db: DBSession, user: Usuario, session_id: str) -> SessoesModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s, db)

    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finalizado_em = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def upsert_summary(
    db: DBSession,
    user: Usuario,
    session_id: str,
    reps: int,
    rom: float,
    cadence: float | None,
    alerts: list,
) -> ResumoSessaoModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    summary = db.execute(select(ResumoSessaoModel).where(ResumoSessaoModel.sessao_id == session_id)).scalar_one_or_none()

    if summary:
        summary.repeticoes = reps
        summary.adm = rom
        summary.cadencia = cadence
        summary.alertas = alerts
    else:
        summary = ResumoSessaoModel(
            sessao_id=session_id,
            repeticoes=reps,
            adm=rom,
            cadencia=cadence,
            alertas=alerts,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary


def get_summary(db: DBSession, user: Usuario, session_id: str) -> ResumoSessaoModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s)

    summary = db.execute(
        select(ResumoSessaoModel).where(ResumoSessaoModel.sessao_id == session_id)
    ).scalar_one_or_none()
    if not summary:
        raise SessionNotFoundError("Resumo não encontrado.")
    return summary


def finalize_session(
    db: DBSession,
    user: Usuario,
    session_id: str,
    reps: int | None,
    rom: float | None,
    cadence: float | None,
    alerts: list | None,
) -> SessoesModel:
    s = get_session(db, session_id)
    ensure_session_access(user, s, db)

    has_any = any(v is not None for v in [reps, rom, cadence, alerts])
    if has_any:
        summary = db.execute(select(ResumoSessaoModel).where(ResumoSessaoModel.sessao_id == session_id)).scalar_one_or_none()
        if not summary:
            summary = ResumoSessaoModel(
                sessao_id=session_id, repeticoes=0, adm=0.0, cadencia=None, alertas=[]
            )
            db.add(summary)

        if reps is not None:
            summary.repeticoes = reps
        if rom is not None:
            summary.adm = rom
        if cadence is not None:
            summary.cadencia = cadence
        if alerts is not None:
            summary.alertas = alerts

    if s.status != "FINISHED":
        s.status = "FINISHED"
        s.finalizado_em = datetime.utcnow()

    db.add(s)
    db.commit()
    db.refresh(s)
    return s
