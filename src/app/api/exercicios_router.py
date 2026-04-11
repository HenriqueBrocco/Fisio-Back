from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual, exigir_permissao
from app.db.session import get_db
from app.models.exercicio import Exercicios
from app.models.usuario import Usuario
from app.schemas.exercicio import ExercicioCreate, ExercicioOut, ExercicioUpdate

exercicios_router = APIRouter(prefix="/exercicios", tags=["Exercícios"])


@exercicios_router.post("", response_model=ExercicioOut, status_code=status.HTTP_201_CREATED)
def create_exercise(payload: ExercicioCreate, db: DBSession = Depends(get_db), user: Usuario = Depends(get_usuario_atual), _=Depends(exigir_permissao("PRO")),):
    ex = Exercicios(
        autor_usuario_id=user.id,
        titulo=payload.titulo,
        descricao=payload.descricao or "",
        foco_corporal=payload.foco_corporal,
        tipo_analise=payload.tipo_analise,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@exercicios_router.get("", response_model=list[ExercicioOut])
def list_exercises(
    db: DBSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    return db.execute(select(Exercicios).offset(skip).limit(limit)).scalars().all()


@exercicios_router.get("/{exercise_id}", response_model=ExercicioOut)
def get_exercise(exercise_id: int, db: DBSession = Depends(get_db)):
    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")
    return ex


@exercicios_router.put("/{exercise_id}", response_model=ExercicioOut)
def update_exercise(
    exercise_id: int,
    payload: ExercicioUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
):
    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    if payload.titulo is not None:
        ex.titulo = payload.titulo
    if payload.descricao is not None:
        ex.description = payload.descricao
    if payload.foco_corporal is not None:
        ex.foco_corporal = payload.foco_corporal
    if payload.tipo_analise is not None:
        ex.tipo_analise = payload.tipo_analise

    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@exercicios_router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
):
    ex = db.execute(select(Exercicios).where(Exercicios.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    db.delete(ex)
    db.commit()
    return None
