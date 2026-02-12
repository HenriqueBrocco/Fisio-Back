from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.session import Session as SessionModel
from app.models.exercise import Exercise
from app.models.assignment import Assignment
from app.models.user import User
from app.schemas.session import SessionCreate, SessionOut
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/patients", tags=["patient-sessions"])


@router.post("/{patient_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_patient_session(
    patient_id: str,
    payload: SessionCreate,
    db: DBSession = Depends(get_db),
    _=Depends(require_role("PRO")),
):
    # 1) garante que o paciente existe e é PATIENT
    patient = db.execute(select(User).where(User.id == patient_id)).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if patient.role != "PATIENT":
        raise HTTPException(status_code=400, detail="user_id informado não é um paciente.")

    # 2) garante que o exercício existe
    ex = db.execute(select(Exercise).where(Exercise.id == payload.exercise_id)).scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="exercise_id não encontrado.")

    # 3) garante que o assignment existe e pertence ao paciente e ao exercício
    asg = db.execute(select(Assignment).where(Assignment.id == payload.assignment_id)).scalar_one_or_none()
    if not asg:
        raise HTTPException(status_code=404, detail="assignment_id não encontrado.")

    if asg.patient_user_id != patient_id:
        raise HTTPException(status_code=400, detail="assignment_id não pertence a este paciente.")
    if asg.exercise_id != payload.exercise_id:
        raise HTTPException(status_code=400, detail="assignment_id não pertence a este exercício.")

    # 4) cria a sessão
    s = SessionModel(
        patient_user_id=patient_id,
        exercise_id=payload.exercise_id,
        assignment_id=payload.assignment_id,
        config_snapshot=payload.config_snapshot,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("/{patient_id}/sessions", response_model=list[SessionOut])
def list_patient_sessions(
    patient_id: str,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # PRO vê qualquer paciente; PATIENT só vê o próprio
    if user.role == "PATIENT" and user.id != patient_id:
        raise HTTPException(status_code=403, detail="Sem permissão")

    sessions = db.execute(
        select(SessionModel).where(SessionModel.patient_user_id == patient_id)
    ).scalars().all()
    return sessions
