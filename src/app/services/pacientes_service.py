from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.security import hash_password
from app.models.usuario import Usuario
from app.services.ownership import ensure_pro_owns_patient


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def create_patient(db: DBSession, pro_user: Usuario, name: str, email: str, password: str) -> Usuario:
    exists = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
    if exists:
        raise ConflictError("Email já cadastrado.")

    patient = Usuario(
        perfil="PATIENT",
        nome=name,
        email=email,
        senha_hash=hash_password(password),
        usuario_pro_id=pro_user.id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def list_patients(db: DBSession, pro_user: Usuario, skip: int = 0, limit: int = 50) -> list[Usuario]:
    q = (
        select(Usuario)
        .where(Usuario.perfil == "PATIENT", Usuario.usuario_pro_id == pro_user.id)
        .order_by(Usuario.criado_em.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.execute(q).scalars().all()


def get_patient(db: DBSession, pro_user: Usuario, patient_id: str) -> Usuario:
    patient = db.execute(select(Usuario).where(Usuario.id == patient_id, Usuario.perfil == "PATIENT")).scalar_one_or_none()
    if not patient:
        raise NotFoundError("Paciente não encontrado.")
    ensure_pro_owns_patient(pro_user, patient)
    return patient


def update_patient(db: DBSession, user: Usuario, patient_id: str, name: str | None, email: str | None, password: str | None) -> Usuario:
    patient = get_patient(db, user, patient_id)

    if email and email != patient.email:
        exists = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
        if exists:
            raise ConflictError("Email já cadastrado.")
        patient.email = email

    if name is not None:
        patient.nome = name
    if password is not None:
        patient.senha_hash = hash_password(password)

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: DBSession, user_id: Usuario, patient_id: str) -> None:
    patient = get_patient(db, user_id, patient_id)
    db.delete(patient)
    db.commit()
