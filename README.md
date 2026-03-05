# Fisio Backend (TCC)

Backend em **FastAPI** para o aplicativo do TCC.

## Stack
- Python 3.11
- FastAPI + Uvicorn
- PostgreSQL
- SQLAlchemy + Alembic (migrations)

## Estrutura de pastas (resumo)
- `src/app/main.py` — inicialização da API
- `src/app/api/` — rotas (endpoints)
- `src/app/models/` — modelos SQLAlchemy
- `src/app/schemas/` — schemas Pydantic (request/response)
- `src/app/db/` — sessão/engine/base do banco
- `alembic/` — migrations

### 1 - Pré-requisitos
- Docker Desktop
- Python 3.11+
- (Opcional) DBeaver

### 2 - Configurar variáveis
- Windows:
Crie um `.env` a partir do `.env.example`:

- Linux/Mac:
    cp .env.example .env

### 3 - Rodar tudo com Docker (API + Postgres)
```bash
docker compose up -d --build
```

- Verifique se o container está saudável:
```bash
docker ps
```

### 4 - Criar venv e instalar dependências
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 5 - Rodar migrations
```bash
docker compose exec api alembic upgrade head
```

### 6 - Criar um usuário PRO (admin)
```bash
docker compose exec api python -m scripts.create_pro
```

### Se quiser subir a API pelo vs, mas já está rodando pelo docker
```bash
python -m uvicorn app.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
```

# Docs: http://localhost:8000/docs
# DB (para DBeaver): host 127.0.0.1, porta 5433, db fisio, user fisio, senha fisio

### Testes
```bash
pytest -q
```

### WebSocket stream test (com frame)

1) Coloque um frame JPEG em `tests/assets/frame.jpg` (uma foto com uma pessoa visível ajuda a gerar métricas).
2) Suba a API localmente.
3) Rode:

```powershell
pip install requests websocket-client
$env:TEST_PRO_EMAIL='admin@admin.com'
$env:TEST_PRO_PASSWORD='123456'
python -m scripts.ws_stream_test
```