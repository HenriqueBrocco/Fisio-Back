from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.assignment import Assignment
from app.models.exercise import Exercise
from app.models.session import Session as SessionModel
from app.models.user import User


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


def create_session_for_patient(
    db: DBSession,
    patient_id: str,
    exercise_id: int,
    assignment_id: int,
    config_snapshot: dict,
) -> SessionModel:
    patient = db.execute(select(User).where(User.id == patient_id)).scalar_one_or_none()
    if not patient:
        raise NotFoundError("Paciente não encontrado.")
    if patient.role != "PATIENT":
        raise BadRequestError("user_id informado não é um paciente.")

    ex = db.execute(select(Exercise).where(Exercise.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("exercise_id não encontrado.")

    asg = db.execute(select(Assignment).where(Assignment.id == assignment_id)).scalar_one_or_none()
    if not asg:
        raise NotFoundError("assignment_id não encontrado.")

    if asg.patient_user_id != patient_id:
        raise BadRequestError("assignment_id não pertence a este paciente.")
    if asg.exercise_id != exercise_id:
        raise BadRequestError("assignment_id não pertence a este exercício.")

    s = SessionModel(
        patient_user_id=patient_id,
        exercise_id=exercise_id,
        assignment_id=assignment_id,
        config_snapshot=config_snapshot,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_sessions_for_patient(db: DBSession, user: User, patient_id: str) -> list[SessionModel]:
    # PRO vê qualquer; PATIENT só vê o próprio
    if user.role == "PATIENT" and user.id != patient_id:
        raise BadRequestError("Sem permissão")

    sessions = (
        db.execute(select(SessionModel).where(SessionModel.patient_user_id == patient_id))
        .scalars()
        .all()
    )
    return sessions
