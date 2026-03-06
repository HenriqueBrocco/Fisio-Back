from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.session import SessionCreate, SessionOut
from app.services.patient_sessions_service import (
    BadRequestError,
    NotFoundError,
    create_session_for_patient,
    list_sessions_for_patient,
)

router = APIRouter(prefix="/patients", tags=["patient-sessions"])


@router.post(
    "/{patient_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED
)
def create_patient_session(
    patient_id: str,
    payload: SessionCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    try:
        return create_session_for_patient(
            db=db,
            patient_id=patient_id,
            exercise_id=payload.exercise_id,
            assignment_id=payload.assignment_id,
            config_snapshot=payload.config_snapshot,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{patient_id}/sessions", response_model=list[SessionOut])
def list_patient_sessions(
    patient_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return list_sessions_for_patient(db, user, patient_id)
    except BadRequestError as e:
        # permissão
        if str(e) == "Sem permissão":
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
