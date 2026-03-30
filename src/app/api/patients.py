from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services.ownership import OwnershipError
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
    user: User = Depends(get_current_user),
    _=Depends(require_role("PRO")),
):
    try:
        return create_patient(db, user, payload.name, payload.email, payload.password)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[PatientOut])
def list_patients_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
    user: User = Depends(get_current_user),
):
    return list_patients(db, user, skip=skip, limit=limit)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
    user: User = Depends(get_current_user),
):
    try:
        return get_patient(db, user, patient_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient_endpoint(
    patient_id: str,
    payload: PatientUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
    user: User = Depends(get_current_user),
):
    try:
        return update_patient(
            db=db,
            user=user,
            patient_id=patient_id,
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
    user: User = Depends(get_current_user),
):
    try:
        delete_patient(db, user, patient_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
