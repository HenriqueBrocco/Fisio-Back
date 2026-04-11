from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BodyFocus = Literal["TRUNK", "UPPER", "LOWER"]


class ExercicioCreate(BaseModel):
    titulo: str = Field(..., max_length=120)
    descricao: str | None = Field(default="", max_length=1000)
    foco_corporal: BodyFocus = "TRUNK"
    tipo_analise: str = Field(default="V1_LITE_THRESHOLDS", max_length=40)


class ExercicioUpdate(BaseModel):
    titulo: str | None = Field(None, max_length=120)
    descricao: str | None = Field(None, max_length=1000)
    foco_corporal: BodyFocus | None = None
    tipo_analise: str | None = Field(None, max_length=40)


class ExercicioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autor_usuario_id: str
    titulo: str
    descricao: str
    foco_corporal: str
    tipo_analise: str
    criado_em: datetime
