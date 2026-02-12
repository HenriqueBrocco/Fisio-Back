from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.models.exercise import Exercise
from app.models.assignment import Assignment, ExerciseConfig
from app.schemas.assignment import (
    ExerciseConfigCreate, ExerciseConfigOut,
    AssignmentCreate, AssignmentUpdate, AssignmentOut,
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


# -------------------------
# ExerciseConfig endpoints
# -------------------------

@router.post("/configs", response_model=ExerciseConfigOut, status_code=status.HTTP_201_CREATED)
def create_exercise_config(
    payload: ExerciseConfigCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    # valida FK de exercise e patient
    ex = db.execute(select(Exercise).where(Exercise.id == payload.exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="exercise_id não encontrado")

    patient = db.execute(select(User).where(User.id == payload.patient_user_id)).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="patient_user_id não encontrado")

    cfg = ExerciseConfig(
        exercise_id=payload.exercise_id,
        patient_user_id=payload.patient_user_id,
        params=payload.params,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("/configs", response_model=list[ExerciseConfigOut])
def list_configs(
    db: DBSession = Depends(get_db),
    patient_user_id: str | None = None,
    exercise_id: int | None = None,
):
    q = select(ExerciseConfig)
    if patient_user_id:
        q = q.where(ExerciseConfig.patient_user_id == patient_user_id)
    if exercise_id is not None:
        q = q.where(ExerciseConfig.exercise_id == exercise_id)
    return db.execute(q).scalars().all()


@router.get("/configs/{config_id}", response_model=ExerciseConfigOut)
def get_config(config_id: int, db: DBSession = Depends(get_db)):
    cfg = db.execute(select(ExerciseConfig).where(ExerciseConfig.id == config_id)).scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="Config não encontrada")
    return cfg


# -------------------------
# Assignment endpoints
# -------------------------

@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    # valida exercise
    ex = db.execute(select(Exercise).where(Exercise.id == payload.exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="exercise_id não encontrado")

    # valida patient
    patient = db.execute(select(User).where(User.id == payload.patient_user_id)).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="patient_user_id não encontrado")

    # valida config existe e pertence ao mesmo patient+exercise
    cfg = db.execute(select(ExerciseConfig).where(ExerciseConfig.id == payload.config_id)).scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="config_id não encontrado")

    if cfg.patient_user_id != payload.patient_user_id or cfg.exercise_id != payload.exercise_id:
        raise HTTPException(status_code=400, detail="config_id não pertence ao patient/exercise informado")

    a = Assignment(
        patient_user_id=payload.patient_user_id,
        exercise_id=payload.exercise_id,
        config_id=payload.config_id,
        schedule=payload.schedule,
        active=payload.active,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.get("", response_model=list[AssignmentOut])
def list_assignments(
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
    patient_user_id: str | None = None,
):
    # PRO pode listar qualquer um; PATIENT só lista o próprio
    q = select(Assignment)
    if user.role == "PATIENT":
        q = q.where(Assignment.patient_user_id == user.id)
    elif patient_user_id:
        q = q.where(Assignment.patient_user_id == patient_user_id)

    return db.execute(q).scalars().all()


@router.get("/{assignment_id}", response_model=AssignmentOut)
def get_assignment(
    assignment_id: int,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    a = db.execute(select(Assignment).where(Assignment.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment não encontrado")

    if user.role == "PATIENT" and a.patient_user_id != user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")

    return a


@router.put("/{assignment_id}", response_model=AssignmentOut)
def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    a = db.execute(select(Assignment).where(Assignment.id == assignment_id)).scalar_one_or_none()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment não encontrado")

    if payload.config_id is not None:
        cfg = db.execute(select(ExerciseConfig).where(ExerciseConfig.id == payload.config_id)).scalar_one_or_none()
        if not cfg:
            raise HTTPException(status_code=404, detail="config_id não encontrado")
        # garante coerência com patient/exercise
        if cfg.patient_user_id != a.patient_user_id or cfg.exercise_id != a.exercise_id:
            raise HTTPException(status_code=400, detail="config_id não pertence ao patient/exercise do assignment")
        a.config_id = payload.config_id

    if payload.schedule is not None:
        a.schedule = payload.schedule
    if payload.active is not None:
        a.active = payload.active

    db.add(a)
    db.commit()
    db.refresh(a)
    return a
