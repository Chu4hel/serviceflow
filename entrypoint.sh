#!/bin/bash
set -e

echo "Ожидание готовности базы данных..."
# Эта команда будет ждать, пока порт 5432 на хосте db не станет доступен
# Мы добавим netcat в Dockerfile
while ! nc -z db 5432; do
  sleep 0.1
done
echo "База данных готова."

echo "Установка/обновление зависимостей..."
poetry install --no-interaction --no-root

echo "Выполнение миграций базы данных..."
poetry run alembic upgrade head

echo "Запуск сервера..."
# exec "$@" выполнит команду, переданную в docker-compose (т.е. uvicorn)
exec "$@"
