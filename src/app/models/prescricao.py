from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExercicioConfig(Base):
    __tablename__ = "exercicio_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercicio_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercicios.id"))
    paciente_usuario_id: Mapped[str] = mapped_column(String, ForeignKey("usuarios.id"))

    # Deixa flexível em JSON pra amputação / futuro:
    parametros: Mapped[dict] = mapped_column(JSON, default=dict)

    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prescricoes(Base):
    __tablename__ = "prescricoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_usuario_id: Mapped[str] = mapped_column(String, ForeignKey("usuarios.id"))
    exercicio_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercicios.id"))
    config_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercicio_configs.id"))

    frequencia: Mapped[str] = mapped_column(String(30), default="DAILY")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
