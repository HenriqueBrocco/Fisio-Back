from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut
from app.api.deps import require_role

import hashlib

router = APIRouter(prefix="/patients", tags=["patients"])

def hash_password(password: str) -> str:
    # Simples por enquanto (sem auth). Depois trocamos por passlib/bcrypt.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db), _=Depends(require_role("PRO"))):
    # email único
    exists = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    patient = User(
        role="PATIENT",
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientOut])
def list_patients(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), _=Depends(require_role("PRO"))):
    q = select(User).where(User.role == "PATIENT").offset(skip).limit(limit)
    patients = db.execute(q).scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db), _=Depends(require_role("PRO"))):
    patient = db.execute(
        select(User).where(User.id == patient_id, User.role == "PATIENT")
    ).scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db), _=Depends(require_role("PRO"))):
    patient = db.execute(
        select(User).where(User.id == patient_id, User.role == "PATIENT")
    ).scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    if payload.email and payload.email != patient.email:
        exists = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
        if exists:
            raise HTTPException(status_code=409, detail="Email já cadastrado.")

    if payload.name is not None:
        patient.name = payload.name
    if payload.email is not None:
        patient.email = payload.email
    if payload.password is not None:
        patient.password_hash = hash_password(payload.password)

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: str, db: Session = Depends(get_db), _=Depends(require_role("PRO"))):
    patient = db.execute(
        select(User).where(User.id == patient_id, User.role == "PATIENT")
    ).scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    db.delete(patient)
    db.commit()
    return None
