from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.prescricao import Prescricoes, ExercicioConfig
from app.models.exercicio import Exercicios
from app.models.sessao import Sessoes as SessoesModel
from app.models.usuario import Usuario
from app.services.ownership import OwnershipError, ensure_pro_owns_patient


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


def create_session_for_patient(db: DBSession, patient_id: str, exercise_id: int, assignment_id: int, config_snapshot: dict, pro_user: Usuario,) -> SessoesModel:
    patient = db.execute(select(Usuario).where(Usuario.id == patient_id)).scalar_one_or_none()
    if pro_user.perfil == "PRO":
        ensure_pro_owns_patient(pro_user, patient)
    if not patient:
        raise NotFoundError("Paciente não encontrado.")
    if patient.perfil != "PATIENT":
        raise BadRequestError("usuario_id informado não é um paciente.")

    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise NotFoundError("exercicio_id não encontrado.")

    asg = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not asg:
        raise NotFoundError("prescricao_id não encontrado.")

    if asg.paciente_usuario_id != patient_id:
        raise BadRequestError("prescricao_id não pertence a este paciente.")
    if asg.exercicio_id != exercise_id:
        raise BadRequestError("prescricao_id não pertence a este exercício.")

    s = SessoesModel(
        paciente_usuario_id=patient_id,
        exercicio_id=exercise_id,
        prescricao_id=assignment_id,
        config_snapshot=config_snapshot,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_sessions_for_patient(db: DBSession, user: Usuario, patient_id: str) -> list[SessoesModel]:
    if user.perfil == "PRO":
        patient = db.execute(select(Usuario).where(Usuario.id == patient_id)).scalar_one_or_none()
        if not patient:
            raise NotFoundError("Paciente não encontrado.")
        ensure_pro_owns_patient(user, patient)
    if user.perfil == "PATIENT" and user.id != patient_id:
        raise BadRequestError("Sem permissão")

    sessions = (db.execute(select(SessoesModel).where(SessoesModel.paciente_usuario_id == patient_id)).scalars().all())
    return sessions


def create_session_from_assignment(db: DBSession, user: Usuario, assignment_id: int,) -> SessoesModel:
    asg = db.execute(select(Prescricoes).where(Prescricoes.id == assignment_id)).scalar_one_or_none()
    if not asg:
        raise NotFoundError("Prescrição não encontrada.")

    patient = db.execute(select(Usuario).where(Usuario.id == asg.paciente_usuario_id)).scalar_one_or_none()
    if not patient or patient.perfil != "PATIENT":
        raise NotFoundError("Paciente da prescrição não encontrado.")

    # PATIENT só pode criar sessão para si mesmo
    if user.perfil == "PATIENT" and user.id != asg.paciente_usuario_id:
        raise BadRequestError("Sem permissão")

    # PRO só pode criar sessão para paciente que ele possui
    if user.perfil == "PRO":
        try:
            ensure_pro_owns_patient(user, patient)
        except OwnershipError:
            raise BadRequestError("Sem permissão")

    cfg = db.execute(select(ExercicioConfig).where(ExercicioConfig.id == asg.config_id)).scalar_one_or_none()
    if not cfg:
        raise NotFoundError("Config da prescrição não encontrada.")

    s = SessoesModel(
        paciente_usuario_id=asg.paciente_usuario_id,
        exercicio_id=asg.exercicio_id,
        prescricao_id=asg.id,
        config_snapshot=cfg.parametros or {},
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
