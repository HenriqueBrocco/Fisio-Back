from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_by_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(1000), default="")
    body_focus: Mapped[str] = mapped_column(String(30), default="TRUNK")  # TRUNK/UPPER/LOWER
    analysis_kind: Mapped[str] = mapped_column(String(40), default="V1_LITE_THRESHOLDS")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
