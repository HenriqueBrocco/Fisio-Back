from fastapi import FastAPI
from app.api import infer, sessions
from fastapi.middleware.cors import CORSMiddleware
#from app.db.session import engine, Base
#from app.models import user, exercise, assignment, session  # noqa: F401
from app.api.health import router as health_router
from app.api.patients import router as patients_router
from dotenv import load_dotenv
from app.api.router import api_router

load_dotenv()  # vai ler .env da raiz (cwd)

app = FastAPI(title="Fisio API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # se usar Vite
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5353",
        "http://127.0.0.1:4321",
        "http://127.0.0.1:51439",
        "http://127.0.0.1:5173",
        "http://127.0.0.1",       # Flutter Web dev server
        "http://localhost",       # Flutter Web dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(api_router)
app.include_router(infer.router, prefix="/v1/infer", tags=["infer"])
app.include_router(sessions.router, prefix="/v1/sessions", tags=["sessions"])
#app.include_router(health_router)
#app.include_router(patients_router)