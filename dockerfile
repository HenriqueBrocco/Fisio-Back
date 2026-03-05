FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# deps do sistema (psycopg + opencv/mediapipe podem precisar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Instala requirements
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/ml.txt

# Copia o código
COPY . .

EXPOSE 8000

# roda uvicorn com app-dir src (igual você faz local)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
