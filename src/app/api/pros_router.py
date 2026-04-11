from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencias import exigir_permissao
from app.core.security import hash_password
from app.db.session import get_db
from app.models.usuario import Usuario

router = APIRouter(prefix="/pros", tags=["Profissinais"])


class ProCreate(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class ProOut(BaseModel):
    id: str
    role: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


@router.post("", response_model=ProOut, status_code=status.HTTP_201_CREATED)
def create_pro(payload: ProCreate, db: Session = Depends(get_db), _=Depends(exigir_permissao("PRO"))):
    exists = db.execute(select(Usuario).where(Usuario.email == payload.email)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    pro = Usuario(
        role="PRO",
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(pro)
    db.commit()
    db.refresh(pro)
    return pro
