from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseOut
from app.api.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.post("", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
def create_exercise(
    payload: ExerciseCreate,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _=Depends(require_role("PRO")),
):
    ex = Exercise(
        created_by_user_id=user.id,
        title=payload.title,
        description=payload.description or "",
        body_focus=payload.body_focus,
        analysis_kind=payload.analysis_kind,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.get("", response_model=list[ExerciseOut])
def list_exercises(
    db: DBSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    return db.execute(select(Exercise).offset(skip).limit(limit)).scalars().all()


@router.get("/{exercise_id}", response_model=ExerciseOut)
def get_exercise(exercise_id: int, db: DBSession = Depends(get_db)):
    ex = db.execute(select(Exercise).where(Exercise.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")
    return ex


@router.put("/{exercise_id}", response_model=ExerciseOut)
def update_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    ex = db.execute(select(Exercise).where(Exercise.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    if payload.title is not None:
        ex.title = payload.title
    if payload.description is not None:
        ex.description = payload.description
    if payload.body_focus is not None:
        ex.body_focus = payload.body_focus
    if payload.analysis_kind is not None:
        ex.analysis_kind = payload.analysis_kind

    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    ex = db.execute(select(Exercise).where(Exercise.id == exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercício não encontrado.")

    db.delete(ex)
    db.commit()
    return None
