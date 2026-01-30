from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

# Ajuste o import abaixo para o seu projeto:
# - se você tiver app.db.session.get_db, use isso
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    return {"status": "ok"}

@router.get("/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
