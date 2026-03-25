from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.assignment import ExerciseConfig
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise_params import KneeExtensionV1Params
from app.services.ownership import OwnershipError, ensure_pro_owns_patient


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


PARAM_SCHEMAS = {
    "KNEE_EXTENSION_V1": KneeExtensionV1Params,
}


def update_config_params(
    db: DBSession, pro_user: User, config_id: int, params: dict
) -> ExerciseConfig:
    cfg = db.execute(
        select(ExerciseConfig).where(ExerciseConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config não encontrada.")

    patient = db.execute(select(User).where(User.id == cfg.patient_user_id)).scalar_one_or_none()
    if not patient:
        raise NotFoundError("Paciente da config não encontrado.")
    try:
        ensure_pro_owns_patient(pro_user, patient)
    except OwnershipError:
        raise BadRequestError("Sem permissão para este paciente")

    ex = db.execute(select(Exercise).where(Exercise.id == cfg.exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("Exercício da config não encontrado.")

    schema = PARAM_SCHEMAS.get(ex.analysis_kind)
    if not schema:
        raise BadRequestError(f"analysis_kind não suportado para params: {ex.analysis_kind}")

    validated = schema(**params).model_dump()
    cfg.params = validated

    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
