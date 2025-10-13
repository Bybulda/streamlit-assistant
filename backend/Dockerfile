FROM python:3.11-slim

WORKDIR /app

# 🧰 Устанавливаем необходимые системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential g++ netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# 📄 Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📂 Копируем исходники
COPY . /app/backend
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# 🧠 PYTHONPATH, чтобы backend был импортируемым модулем
ENV PYTHONPATH=/app


CMD alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000

