from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SummaryIn(BaseModel):
    user_id: str
    exercise_id: str
    reps_valid: int
    reps_total: int
    rom_avg: float
    rom_peak: float
    cadence_avg: float | None = None
    notes: list[str] = []

@router.post("/summary")
async def save_summary(payload: SummaryIn):
    # TODO: persistir em banco/arquivo
    return {"status": "saved", "summary": payload.model_dump()}