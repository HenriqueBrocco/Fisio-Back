from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

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
    schedule: str | None = Field(None, max_length=30)
    active: bool | None = None
    config_id: int | None = None


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_user_id: str
    exercise_id: int
    config_id: int
    schedule: str
    active: bool
    created_at: datetime


class ConfigParamsUpdate(BaseModel):
    params: dict[str, Any]
