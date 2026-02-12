from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid

from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id"))
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("assignments.id"))

    status: Mapped[str] = mapped_column(String(20), default="CREATED")  # CREATED/RUNNING/FINISHED
    config_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class SessionSummary(Base):
    __tablename__ = "session_summaries"

    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), primary_key=True)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    rom: Mapped[float] = mapped_column(Float, default=0.0)
    cadence: Mapped[float | None] = mapped_column(Float, nullable=True)
    alerts: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
