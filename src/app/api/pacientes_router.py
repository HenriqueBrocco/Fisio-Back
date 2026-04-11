from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual, exigir_permissao
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate
from app.services.ownership import OwnershipError
from app.services.pacientes_service import (
    ConflictError,
    NotFoundError,
    create_patient,
    delete_patient,
    get_patient,
    list_patients,
    update_patient,
)

pacientes_router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@pacientes_router.post("", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(payload: PacienteCreate, db: DBSession = Depends(get_db), user: Usuario = Depends(get_usuario_atual), _=Depends(exigir_permissao("PRO")),):
    try:
        return create_patient(db, user, payload.nome, payload.email, payload.password)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))



@pacientes_router.get("", response_model=list[PacienteOut])
def list_patients_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    return list_patients(db, user, skip=skip, limit=limit)


@pacientes_router.get("/{patient_id}", response_model=PacienteOut)
def get_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return get_patient(db, user, patient_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")


@pacientes_router.put("/{patient_id}", response_model=PacienteOut)
def update_patient_endpoint(
    patient_id: str,
    payload: PacienteUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return update_patient(
            db=db,
            user=user,
            patient_id=patient_id,
            name=payload.nome,
            email=payload.email,
            password=payload.password,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")


@pacientes_router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_endpoint(
    patient_id: str,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        delete_patient(db, user, patient_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OwnershipError:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
