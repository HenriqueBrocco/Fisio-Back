from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

router = APIRouter()
_SUMMARIES = []  # memória (MVP)

class SummaryIn(BaseModel):
    user_id: str
    exercise_id: str
    session_id: str
    reps_valid: int
    reps_total: int
    rom_avg: float
    rom_peak: float
    cadence_avg: float | None = None
    notes: list[str] = []

class SummaryOut(BaseModel):
    summary_id: str
    created_at: str
    data: SummaryIn

@router.post("/summary", response_model=SummaryOut)
async def save_summary(payload: SummaryIn):
    item = SummaryOut(
        summary_id=str(uuid4()),
        created_at=datetime.utcnow().isoformat() + "Z",
        data=payload
    )
    _SUMMARIES.append(item)
    return item