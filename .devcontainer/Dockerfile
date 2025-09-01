FROM mcr.microsoft.com/devcontainers/python:1-3.13

# Устанавливаем netcat для проверки доступности БД
RUN apt-get update && apt-get install -y netcat-openbsd

ARG USERNAME=vscode

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

COPY app/ /app/app

# Копируем и делаем entrypoint исполняемым
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R ${USERNAME}:${USERNAME} /app

