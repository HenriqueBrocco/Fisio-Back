from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.deps import require_role
from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services.patients_service import (
    ConflictError,
    NotFoundError,
    create_patient,
    delete_patient,
    get_patient,
    list_patients,
    update_patient,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    payload: PatientCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return create_patient(db, payload.name, payload.email, payload.password)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[PatientOut])
def list_patients_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    return list_patients(db, skip=skip, limit=limit)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return get_patient(db, patient_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient_endpoint(
    patient_id: str,
    payload: PatientUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return update_patient(
            db=db,
            patient_id=patient_id,
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        delete_patient(db, patient_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
