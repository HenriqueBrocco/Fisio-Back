import os
import pytest
from fastapi.testclient import TestClient

# Import do app (lembrando: seu app está em src/)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # Garante que DATABASE_URL existe nos testes
    assert os.getenv("DATABASE_URL"), "DATABASE_URL não definido no ambiente de teste"
    return TestClient(app)
