from fastapi import FastAPI
from app.api import infer, session

app = FastAPI(title="Fisio API", version="0.1.0")

# Rotas
app.include_router(infer.router, prefix="/v1/infer", tags=["infer"])
app.include_router(session.router, prefix="/v1/session", tags=["session"])

@app.get("/health")
def health():
    return {"status": "ok"}