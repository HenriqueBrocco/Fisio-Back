from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.security import hash_password
from app.models.user import User


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def create_patient(db: DBSession, name: str, email: str, password: str) -> User:
    exists = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if exists:
        raise ConflictError("Email já cadastrado.")

    patient = User(
        role="PATIENT",
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def list_patients(db: DBSession, skip: int = 0, limit: int = 50) -> list[User]:
    q = (
        select(User)
        .where(User.role == "PATIENT")
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.execute(q).scalars().all()


def get_patient(db: DBSession, patient_id: str) -> User:
    patient = db.execute(
        select(User).where(User.id == patient_id, User.role == "PATIENT")
    ).scalar_one_or_none()
    if not patient:
        raise NotFoundError("Paciente não encontrado.")
    return patient


def update_patient(
    db: DBSession, patient_id: str, name: str | None, email: str | None, password: str | None
) -> User:
    patient = get_patient(db, patient_id)

    if email and email != patient.email:
        exists = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if exists:
            raise ConflictError("Email já cadastrado.")
        patient.email = email

    if name is not None:
        patient.name = name
    if password is not None:
        patient.password_hash = hash_password(password)

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: DBSession, patient_id: str) -> None:
    patient = get_patient(db, patient_id)
    db.delete(patient)
    db.commit()
