from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Exercicios(Base):
    __tablename__ = "exercicios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    autor_usuario_id: Mapped[str] = mapped_column(String, ForeignKey("usuarios.id"))
    titulo: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str] = mapped_column(String(1000), default="")
    foco_corporal: Mapped[str] = mapped_column(String(30), default="TRUNK")  # TRUNK/UPPER/LOWER
    tipo_analise: Mapped[str] = mapped_column(String(40), default="V1_LITE_THRESHOLDS")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
