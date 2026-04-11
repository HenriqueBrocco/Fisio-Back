import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    perfil: Mapped[str] = mapped_column(String(20), index=True)  # PRO | PATIENT
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario_pro_id: Mapped[str | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True) # nulo se for Pro
    usuario_pro = relationship("Usuario", remote_side="Usuario.id", foreign_keys=[usuario_pro_id])
