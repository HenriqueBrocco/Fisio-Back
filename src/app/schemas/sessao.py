from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessaoCreate(BaseModel):
    exercicio_id: int
    prescricao_id: int
    config_snapshot: dict[str, Any] = Field(default_factory=dict)


class SessaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    paciente_usuario_id: str
    exercicio_id: int
    prescricao_id: int
    status: str
    config_snapshot: dict
    iniciado_em: datetime
    finalizado_em: datetime | None = None


class ResumoSessaoIn(BaseModel):
    repeticoes: int = 0
    adm: float = 0.0  # no seu model está Integer, mas vamos tratar como float no schema
    cadencia: float | None = None
    alertas: list = Field(default_factory=list)


class ResumoSessaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sessao_id: str
    repeticoes: int
    adm: float
    cadencia: float | None = None
    alertas: list
    criado_em: datetime


class SessaoFinalizadaIn(BaseModel):
    repeticoes: int | None = None
    adm: float | None = None
    cadencia: float | None = None
    alertas: list[Any] | None = None
