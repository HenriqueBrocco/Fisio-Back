from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any

class SessionCreate(BaseModel):
    exercise_id: int
    assignment_id: int
    config_snapshot: dict[str, Any] = Field(default_factory=dict)

class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_user_id: str
    exercise_id: int
    assignment_id: int
    status: str
    config_snapshot: dict
    started_at: datetime
    finished_at: Optional[datetime] = None

class SessionSummaryIn(BaseModel):
    reps: int = 0
    rom: float = 0.0  # no seu model está Integer, mas vamos tratar como float no schema
    cadence: Optional[float] = None
    alerts: list = Field(default_factory=list)

class SessionSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    reps: int
    rom: float
    cadence: Optional[float] = None
    alerts: list
    created_at: datetime

class SessionFinalizeIn(BaseModel):
    reps: Optional[int] = None
    rom: Optional[float] = None
    cadence: Optional[float] = None
    alerts: Optional[list[Any]] = None