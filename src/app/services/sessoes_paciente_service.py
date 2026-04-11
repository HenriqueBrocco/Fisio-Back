from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.prescricao import Prescricoes, ExercicioConfig
from app.models.exercicio import Exercicios
from app.models.sessao import Sessoes as SessionModel
from app.models.usuario import Usuario
from app.services.ownership import OwnershipError, ensure_pro_owns_patient


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
    pro_user: Usuario,
) -> SessionModel:
    patient = db.execute(select(Usuario).where(Usuario.id == patient_id)).scalar_one_or_none()
    if pro_user.perfil == "PRO":
        ensure_pro_owns_patient(pro_user, patient)
    if not patient:
        raise NotFoundError("Paciente não encontrado.")
    if patient.perfil != "PATIENT":
        raise BadRequestError("user_id informado não é um paciente.")

    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("exercise_id não encontrado.")

    asg = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not asg:
        raise NotFoundError("assignment_id não encontrado.")

    if asg.paciente_usuario_id != patient_id:
        raise BadRequestError("assignment_id não pertence a este paciente.")
    if asg.exercicio_id != exercise_id:
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


def list_sessions_for_patient(db: DBSession, user: Usuario, patient_id: str) -> list[SessionModel]:
    if user.perfil == "PRO":
        patient = db.execute(select(Usuario).where(Usuario.id == patient_id)).scalar_one_or_none()
        if not patient:
            raise NotFoundError("Paciente não encontrado.")
        ensure_pro_owns_patient(user, patient)
    if user.perfil == "PATIENT" and user.id != patient_id:
        raise BadRequestError("Sem permissão")

    sessions = (
        db.execute(select(SessionModel).where(SessionModel.paciente_usuario_id == patient_id))
        .scalars()
        .all()
    )
    return sessions


def create_session_from_assignment(
    db: DBSession,
    user: Usuario,
    assignment_id: int,
) -> SessionModel:
    asg = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not asg:
        raise NotFoundError("Assignment não encontrado.")

    patient = db.execute(select(Usuario).where(Usuario.id == asg.paciente_usuario_id)).scalar_one_or_none()
    if not patient or patient.perfil != "PATIENT":
        raise NotFoundError("Paciente do assignment não encontrado.")

    # PATIENT só pode criar sessão para si mesmo
    if user.perfil == "PATIENT" and user.id != asg.paciente_usuario_id:
        raise BadRequestError("Sem permissão")

    # PRO só pode criar sessão para paciente que ele possui
    if user.perfil == "PRO":
        try:
            ensure_pro_owns_patient(user, patient)
        except OwnershipError:
            raise BadRequestError("Sem permissão")

    cfg = db.execute(
        select(ExercicioConfig).where(ExercicioConfig.id == asg.config_id)
    ).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config do assignment não encontrada.")

    s = SessionModel(
        patient_user_id=asg.paciente_usuario_id,
        exercise_id=asg.exercicio_id,
        assignment_id=asg.id,
        config_snapshot=cfg.parametros or {},
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
