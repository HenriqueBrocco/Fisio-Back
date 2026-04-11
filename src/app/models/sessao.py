import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sessoes(Base):
    __tablename__ = "sessoes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paciente_usuario_id: Mapped[str] = mapped_column(String, ForeignKey("usuarios.id"))
    exercicio_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercicios.id"))
    prescricao_id: Mapped[int] = mapped_column(Integer, ForeignKey("prescricoes.id"))

    status: Mapped[str] = mapped_column(String(20), default="CREATED")  # CREATED/RUNNING/FINISHED
    config_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)

    iniciado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finalizado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ResumoSessao(Base):
    __tablename__ = "resumos_sessao"

    sessao_id: Mapped[str] = mapped_column(String, ForeignKey("sessoes.id"), primary_key=True)
    repeticoes: Mapped[int] = mapped_column(Integer, default=0)
    adm: Mapped[float] = mapped_column(Float, default=0.0)
    cadencia: Mapped[float | None] = mapped_column(Float, nullable=True)
    alertas: Mapped[list] = mapped_column(JSON, default=list)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
