import app.models # noqa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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