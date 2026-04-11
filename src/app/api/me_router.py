from fastapi import APIRouter, Depends

from app.api.dependencias import get_usuario_atual
from app.models.usuario import Usuario

me_router = APIRouter(tags=["Me"])


@me_router.get("/me")
def me(user: Usuario = Depends(get_usuario_atual)):
    return {
        "id": user.id,
        "role": user.perfil,
        "name": user.nome,
        "email": user.email,
    }
