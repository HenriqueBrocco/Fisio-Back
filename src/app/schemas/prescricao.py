from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

frequencia = Literal["DAILY", "WEEKLY", "CUSTOM"]


class ExercicioConfigCreate(BaseModel):
    exercicio_id: int
    paciente_usuario_id: str
    parametros: dict[str, Any] = Field(default_factory=dict)


class ExercicioConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercicio_id: int
    paciente_usuario_id: str
    parametros: dict
    criado_em: datetime


class PrescricaoCreate(BaseModel):
    paciente_usuario_id: str
    exercicio_id: int
    config_id: int
    frequencia: str = Field(default="DAILY", max_length=30)
    ativo: bool = True


class PrescricaoUpdate(BaseModel):
    frequencia: str | None = Field(None, max_length=30)
    ativo: bool | None = None
    config_id: int | None = None


class PrescricaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paciente_usuario_id: str
    exercicio_id: int
    config_id: int
    frequencia: str
    ativo: bool
    criado_em: datetime


class ConfigParametrosUpdate(BaseModel):
    parametros: dict[str, Any]
