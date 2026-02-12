from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Literal

Schedule = Literal["DAILY", "WEEKLY", "CUSTOM"]

class ExerciseConfigCreate(BaseModel):
    exercise_id: int
    patient_user_id: str
    params: dict[str, Any] = Field(default_factory=dict)

class ExerciseConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    patient_user_id: str
    params: dict
    created_at: datetime


class AssignmentCreate(BaseModel):
    patient_user_id: str
    exercise_id: int
    config_id: int
    schedule: str = Field(default="DAILY", max_length=30)
    active: bool = True

class AssignmentUpdate(BaseModel):
    schedule: Optional[str] = Field(None, max_length=30)
    active: Optional[bool] = None
    config_id: Optional[int] = None

class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_user_id: str
    exercise_id: int
    config_id: int
    schedule: str
    active: bool
    created_at: datetime
