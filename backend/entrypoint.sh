#!/bin/bash
set -e

echo "⏳ Waiting for Postgres..."
until nc -z db 5432; do
  sleep 1
done
echo "✅ Postgres is up!"

echo "🚀 Running Alembic migrations..."
cd /app
alembic upgrade head

echo "✅ Starting backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
