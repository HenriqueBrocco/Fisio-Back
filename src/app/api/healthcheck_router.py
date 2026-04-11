from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

healthcheck_router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])


@healthcheck_router.get("")
def health():
    return {"status": "ok"}


@healthcheck_router.get("/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
