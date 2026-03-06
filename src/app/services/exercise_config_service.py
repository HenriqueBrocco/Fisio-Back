from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.assignment import ExerciseConfig
from app.models.exercise import Exercise
from app.schemas.exercise_params import KneeExtensionV1Params


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


PARAM_SCHEMAS = {
    "KNEE_EXTENSION_V1": KneeExtensionV1Params,
}


def update_config_params(db: DBSession, config_id: int, params: dict) -> ExerciseConfig:
    cfg = db.execute(
        select(ExerciseConfig).where(ExerciseConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config não encontrada.")

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
