FROM mcr.microsoft.com/devcontainers/python:1-3.13

ARG USERNAME=vscode

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

COPY app/ /app/app

RUN chown -R ${USERNAME}:${USERNAME} /app