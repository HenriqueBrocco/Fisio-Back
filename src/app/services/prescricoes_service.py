from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.prescricao import Prescricoes, ExercicioConfig
from app.models.exercicio import Exercicios
from app.models.usuario import Usuario
from app.schemas.exercise_params import KneeExtensionV1Params
from app.services.ownership import OwnershipError, ensure_pro_owns_patient


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


PARAM_SCHEMAS = {
    "KNEE_EXTENSION_V1": KneeExtensionV1Params,
    "V1_LITE_THRESHOLDS": KneeExtensionV1Params,
}

def _get_exercise(db: DBSession, exercise_id: int) -> Exercicios:
    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("exercise_id não encontrado")
    return ex


def _get_patient(db: DBSession, patient_user_id: str, pro_user: Usuario | None = None) -> Usuario:
    patient = db.execute(select(Usuario).where(Usuario.id == patient_user_id)).scalar_one_or_none()
    if not patient:
        raise NotFoundError("patient_user_id não encontrado")
    if patient.perfil != "PATIENT":
        raise BadRequestError("user_id informado não é de um paciente")
    if pro_user is not None and pro_user.perfil == "PRO":
        try:
            ensure_pro_owns_patient(pro_user, patient)
        except OwnershipError:
            raise BadRequestError("Sem permissão para este paciente")
    return patient


def create_exercise_config(db: DBSession, exercise_id: int, patient_user_id: str, params: dict, pro_user: Usuario) -> ExercicioConfig:
    _get_exercise(db, exercise_id)
    _get_patient(db, patient_user_id, pro_user=pro_user)

    cfg = ExercicioConfig(exercicio_id=exercise_id, paciente_usuario_id=patient_user_id, parametros=params,)

    ex = db.execute(select(Exercicios).where(Exercicios.id == cfg.exercicio_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("Exercício da config não encontrado.")
    
    schema = PARAM_SCHEMAS.get(ex.tipo_analise)
    validated = schema(**params).model_dump()
    cfg.parametros = validated

    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def list_configs(db: DBSession, patient_user_id: str | None, exercise_id: int | None) -> list[ExercicioConfig]:
    q = select(ExercicioConfig)
    if patient_user_id:
        q = q.where(ExercicioConfig.paciente_usuario_id == patient_user_id)
    if exercise_id is not None:
        q = q.where(ExercicioConfig.exercicio_id == exercise_id)
    return db.execute(q).scalars().all()


def get_config(db: DBSession, config_id: int) -> ExercicioConfig:
    cfg = db.execute(
        select(ExercicioConfig).where(ExercicioConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config não encontrada")
    return cfg


def update_config_params(db: DBSession, pro_user: Usuario, config_id: int, params: dict) -> ExercicioConfig:
    cfg = db.execute(select(ExercicioConfig).where(ExercicioConfig.id == config_id)).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config não encontrada.")

    patient = db.execute(select(Usuario).where(Usuario.id == cfg.paciente_usuario_id)).scalar_one_or_none()
    if not patient:
        raise NotFoundError("Paciente da config não encontrado.")
    try:
        ensure_pro_owns_patient(pro_user, patient)
    except OwnershipError:
        raise BadRequestError("Sem permissão para este paciente")

    ex = db.execute(select(Exercicios).where(Exercicios.id == cfg.exercicio_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("Exercício da config não encontrado.")

    schema = PARAM_SCHEMAS.get(ex.tipo_analise)
    if not schema:
        raise BadRequestError(f"analysis_kind não suportado para params: {ex.tipo_analise}")

    validated = schema(**params).model_dump(exclude_unset=True)
    parametros_atuais = cfg.parametros or {}

    cfg.parametros = validated
    parametros_atualizados = {**parametros_atuais, **validated}
    cfg.parametros = parametros_atualizados
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def create_assignment(
    db: DBSession,
    patient_user_id: str,
    exercise_id: int,
    config_id: int,
    schedule: str,
    active: bool,
    pro_user: Usuario,
) -> Prescricoes:
    _get_exercise(db, exercise_id)
    _get_patient(db, patient_user_id, pro_user=pro_user)

    cfg = db.execute(
        select(ExercicioConfig).where(ExercicioConfig.id == config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("config_id não encontrado")

    if cfg.paciente_usuario_id != patient_user_id or cfg.exercicio_id != exercise_id:
        raise BadRequestError("config_id não pertence ao patient/exercise informado")

    a = Prescricoes(
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


def list_assignments(db: DBSession, user: Usuario, patient_user_id: str | None) -> list[Prescricoes]:
    q = select(Prescricoes)

    if user.perfil == "PATIENT":
        q = q.where(Prescricoes.paciente_usuario_id == user.id)
    elif patient_user_id:
        q = q.where(Prescricoes.paciente_usuario_id == patient_user_id)

    return db.execute(q).scalars().all()


def get_assignment(db: DBSession, user: Usuario, assignment_id: int) -> Prescricoes:
    a = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise NotFoundError("Assignment não encontrado")

    if user.perfil == "PATIENT" and a.paciente_usuario_id != user.id:
        raise BadRequestError("Sem permissão")

    return a


def update_assignment(
    db: DBSession,
    assignment_id: int,
    schedule: str | None,
    active: bool | None,
    config_id: int | None,
) -> Prescricoes:
    a = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise NotFoundError("Assignment não encontrado")

    if config_id is not None:
        cfg = db.execute(
            select(ExercicioConfig).where(ExercicioConfig.id == config_id)
        ).scalar_one_or_none()
        if not cfg:
            raise NotFoundError("config_id não encontrado")
        if cfg.paciente_usuario_id != a.paciente_usuario_id or cfg.exercicio_id != a.exercicio_id:
            raise BadRequestError("config_id não pertence ao patient/exercise do assignment")
        a.config_id = config_id

    if schedule is not None:
        a.frequencia = schedule
    if active is not None:
        a.ativo = active

    db.add(a)
    db.commit()
    db.refresh(a)
    return a
