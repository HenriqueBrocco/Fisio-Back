from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.assignment import Assignment, ExerciseConfig
from app.models.exercise import Exercise
from app.models.user import User


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


def _get_exercise(db: DBSession, exercise_id: int) -> Exercise:
    ex = db.execute(select(Exercise).where(Exercise.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("exercise_id não encontrado")
    return ex


def _get_patient(db: DBSession, patient_user_id: str) -> User:
    patient = db.execute(select(User).where(User.id == patient_user_id)).scalar_one_or_none()
    if not patient:
        raise NotFoundError("patient_user_id não encontrado")
    if patient.role != "PATIENT":
        raise BadRequestError("user_id informado não é um paciente")
    return patient


def create_exercise_config(
    db: DBSession, exercise_id: int, patient_user_id: str, params: dict
) -> ExerciseConfig:
    _get_exercise(db, exercise_id)
    _get_patient(db, patient_user_id)

    cfg = ExerciseConfig(
        exercise_id=exercise_id,
        patient_user_id=patient_user_id,
        params=params,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def list_configs(
    db: DBSession, patient_user_id: str | None, exercise_id: int | None
) -> list[ExerciseConfig]:
    q = select(ExerciseConfig)
    if patient_user_id:
        q = q.where(ExerciseConfig.patient_user_id == patient_user_id)
    if exercise_id is not None:
        q = q.where(ExerciseConfig.exercise_id == exercise_id)
    return db.execute(q).scalars().all()


def get_config(db: DBSession, config_id: int) -> ExerciseConfig:
    cfg = db.execute(
        select(ExerciseConfig).where(ExerciseConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config não encontrada")
    return cfg


def create_assignment(
    db: DBSession,
    patient_user_id: str,
    exercise_id: int,
    config_id: int,
    schedule: str,
    active: bool,
) -> Assignment:
    _get_exercise(db, exercise_id)
    _get_patient(db, patient_user_id)

    cfg = db.execute(
        select(ExerciseConfig).where(ExerciseConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("config_id não encontrado")

    if cfg.patient_user_id != patient_user_id or cfg.exercise_id != exercise_id:
        raise BadRequestError("config_id não pertence ao patient/exercise informado")

    a = Assignment(
        patient_user_id=patient_user_id,
        exercise_id=exercise_id,
        config_id=config_id,
        schedule=schedule,
        active=active,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def list_assignments(db: DBSession, user: User, patient_user_id: str | None) -> list[Assignment]:
    q = select(Assignment)

    if user.role == "PATIENT":
        q = q.where(Assignment.patient_user_id == user.id)
    elif patient_user_id:
        q = q.where(Assignment.patient_user_id == patient_user_id)

    return db.execute(q).scalars().all()


def get_assignment(db: DBSession, user: User, assignment_id: int) -> Assignment:
    a = db.execute(select(Assignment).where(Assignment.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise NotFoundError("Assignment não encontrado")

    if user.role == "PATIENT" and a.patient_user_id != user.id:
        raise BadRequestError("Sem permissão")

    return a


def update_assignment(
    db: DBSession,
    assignment_id: int,
    schedule: str | None,
    active: bool | None,
    config_id: int | None,
) -> Assignment:
    a = db.execute(select(Assignment).where(Assignment.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise NotFoundError("Assignment não encontrado")

    if config_id is not None:
        cfg = db.execute(
            select(ExerciseConfig).where(ExerciseConfig.id == config_id)
        ).scalar_one_or_none()
        if not cfg:
            raise NotFoundError("config_id não encontrado")
        if cfg.patient_user_id != a.patient_user_id or cfg.exercise_id != a.exercise_id:
            raise BadRequestError("config_id não pertence ao patient/exercise do assignment")
        a.config_id = config_id

    if schedule is not None:
        a.schedule = schedule
    if active is not None:
        a.active = active

    db.add(a)
    db.commit()
    db.refresh(a)
    return a
