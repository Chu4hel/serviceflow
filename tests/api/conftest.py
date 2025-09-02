"""Общие фикстуры для тестов API авторизации."""
import pytest_asyncio
from httpx import AsyncClient

from app.models.serviceflow import User


@pytest_asyncio.fixture(scope="function")
async def user_project(test_user_auth_client: AsyncClient, test_user: User) -> dict:
    """Создает проект для обычного пользователя."""
    response = await test_user_auth_client.post("/manage/projects", json={"name": "User's Project"})
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def second_user_project(second_user_auth_client: AsyncClient, second_user: User) -> dict:
    """Создает проект для второго обычного пользователя."""
    response = await second_user_auth_client.post("/manage/projects", json={"name": "Second User's Project"})
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def superuser_project(superuser_auth_client: AsyncClient, superuser: User) -> dict:
    """Создает проект для суперпользователя."""
    response = await superuser_auth_client.post("/manage/projects", json={"name": "Superuser's Project"})
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def user_service(test_user_auth_client: AsyncClient, user_project: dict) -> dict:
    """Создает услугу в проекте обычного пользователя."""
    project_id = user_project["id"]
    service_data = {"name": "Test Service", "duration_minutes": 60, "price": 100}
    response = await test_user_auth_client.post(f"/manage/projects/{project_id}/services", json=service_data)
    assert response.status_code == 201
    return response.json()
