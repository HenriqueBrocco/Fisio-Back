from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.exc import UnknownHashError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import TokenOut

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger manda "username", então aqui a gente interpreta como email
    user = db.execute(select(Usuario).where(Usuario.email == form.username)).scalar_one_or_none()
    try:
        ok = verify_password(form.password, user.senha_hash)
    except UnknownHashError:
        ok = False

    if not user or not ok:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token(sub=user.id, role=user.perfil)
    return TokenOut(access_token=token)
