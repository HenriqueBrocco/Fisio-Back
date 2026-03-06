from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentOut,
    AssignmentUpdate,
    ExerciseConfigCreate,
    ExerciseConfigOut,
)
from app.services.assignments_service import (
    BadRequestError,
    NotFoundError,
    create_assignment,
    create_exercise_config,
    get_assignment,
    get_config,
    list_assignments,
    list_configs,
    update_assignment,
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


# -------- Exercise Configs --------


@router.post("/configs", response_model=ExerciseConfigOut, status_code=status.HTTP_201_CREATED)
def create_config_endpoint(
    payload: ExerciseConfigCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return create_exercise_config(
            db, payload.exercise_id, payload.patient_user_id, payload.params
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/configs", response_model=list[ExerciseConfigOut])
def list_configs_endpoint(
    db: DBSession = Depends(get_db),
    patient_user_id: str | None = None,
    exercise_id: int | None = None,
):
    return list_configs(db, patient_user_id, exercise_id)


@router.get("/configs/{config_id}", response_model=ExerciseConfigOut)
def get_config_endpoint(config_id: int, db: DBSession = Depends(get_db)):
    try:
        return get_config(db, config_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------- Assignments --------


@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment_endpoint(
    payload: AssignmentCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return create_assignment(
            db=db,
            patient_user_id=payload.patient_user_id,
            exercise_id=payload.exercise_id,
            config_id=payload.config_id,
            schedule=payload.schedule,
            active=payload.active,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[AssignmentOut])
def list_assignments_endpoint(
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
    patient_user_id: str | None = None,
):
    return list_assignments(db, user, patient_user_id)


@router.get("/{assignment_id}", response_model=AssignmentOut)
def get_assignment_endpoint(
    assignment_id: int,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        a = get_assignment(db, user, assignment_id)
        return a
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        # aqui usamos 403 para permissão
        if str(e) == "Sem permissão":
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{assignment_id}", response_model=AssignmentOut)
def update_assignment_endpoint(
    assignment_id: int,
    payload: AssignmentUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return update_assignment(
            db=db,
            assignment_id=assignment_id,
            schedule=payload.schedule,
            active=payload.active,
            config_id=payload.config_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
