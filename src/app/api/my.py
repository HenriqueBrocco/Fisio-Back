from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.patient import PatientOut

router = APIRouter(prefix="/my", tags=["my"])


@router.get("/patients", response_model=list[PatientOut])
def my_patients(
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "PRO":
        raise HTTPException(status_code=403, detail="Sem permissão")

    patients = (
        db.execute(select(User).where(User.role == "PATIENT", User.pro_owner_id == user.id))
        .scalars()
        .all()
    )

    return patients
