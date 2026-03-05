from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BodyFocus = Literal["TRUNK", "UPPER", "LOWER"]


class ExerciseCreate(BaseModel):
    title: str = Field(..., max_length=120)
    description: str | None = Field(default="", max_length=1000)
    body_focus: BodyFocus = "TRUNK"
    analysis_kind: str = Field(default="V1_LITE_THRESHOLDS", max_length=40)


class ExerciseUpdate(BaseModel):
    title: str | None = Field(None, max_length=120)
    description: str | None = Field(None, max_length=1000)
    body_focus: BodyFocus | None = None
    analysis_kind: str | None = Field(None, max_length=40)


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_user_id: str
    title: str
    description: str
    body_focus: str
    analysis_kind: str
    created_at: datetime
