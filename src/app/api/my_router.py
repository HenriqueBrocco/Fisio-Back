from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.paciente import PacienteOut

my_router = APIRouter(prefix="/my", tags=["My"])


@my_router.get("/pacientes", response_model=list[PacienteOut])
def my_patients(
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    if user.perfil != "PRO":
        raise HTTPException(status_code=403, detail="Sem permissão")

    patients = (db.execute(select(Usuario).where(Usuario.perfil == "PATIENT", Usuario.usuario_pro_id == user.id)).scalars().all())

    return patients
