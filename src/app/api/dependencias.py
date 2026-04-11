from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.security import ALGORITHM, SECRET_KEY, decode_access_token
from app.db.session import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_usuario_atual(token: str = Depends(oauth2_scheme), db: DBSession = Depends(get_db)) -> Usuario:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.execute(select(Usuario).where(Usuario.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


def exigir_permissao(role: str):
    def _inner(user: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if user.perfil != role:
            raise HTTPException(status_code=403, detail="Sem permissão")
        return user

    return _inner


def get_usuario_atual_via_token(db: DBSession, token: str) -> Usuario:
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.execute(select(Usuario).where(Usuario.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user
