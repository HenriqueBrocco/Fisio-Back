import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- garante imports do pacote app/ dentro de src/ ---
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

# --- carrega variáveis do .env na raiz do projeto ---
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    # se não tiver python-dotenv instalado, segue só com env do sistema
    pass

from app.models.user import User   # noqa: E402
from app.core.security import hash_password   # noqa: E402


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit(
        "DATABASE_URL não está definido.\n"
        "Crie um arquivo .env na raiz (baseado no .env.example) ou defina a variável no terminal.\n"
        "Exemplo (PowerShell):\n"
        '  $env:DATABASE_URL="postgresql+psycopg://user:pass@127.0.0.1:5432/fisio"\n'
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def main():
    db = SessionLocal()
    try:
        email = input("Email do PRO: ").strip()
        name = input("Nome: ").strip()
        password = input("Senha: ").strip()

        exists = db.query(User).filter(User.email == email).first()
        if exists:
            print("Já existe usuário com esse email.")
            return

        pro = User(
            role="PRO",
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        db.add(pro)
        db.commit()
        print("PRO criado com sucesso!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
