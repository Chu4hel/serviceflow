"""Тесты авторизации для эндпоинтов Подписчиков (/manage/projects/{project_id}/subscribers)."""
import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def user_subscriber(client: AsyncClient, user_project: dict) -> dict:
    """Создает подписчика через публичный API."""
    api_key = user_project["api_key"]
    subscriber_data = {"email": "test.subscriber@example.com"}
    response = await client.post("/public/v1/subscribers", json=subscriber_data, headers={"X-API-KEY": api_key})
    assert response.status_code == 201
    return response.json()


async def test_user_can_get_own_subscriber(test_user_auth_client: AsyncClient, user_project: dict,
                                           user_subscriber: dict):
    """Пользователь может получить своего подписчика."""
    project_id = user_project["id"]
    subscriber_id = user_subscriber["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}/subscribers/{subscriber_id}")
    assert response.status_code == 200
    assert response.json()["id"] == subscriber_id


async def test_user_can_delete_own_subscriber(test_user_auth_client: AsyncClient, user_project: dict,
                                              user_subscriber: dict):
    """Пользователь может удалить своего подписчика."""
    project_id = user_project["id"]
    subscriber_id = user_subscriber["id"]
    response = await test_user_auth_client.delete(f"/manage/projects/{project_id}/subscribers/{subscriber_id}")
    assert response.status_code == 204
    get_response = await test_user_auth_client.get(f"/manage/projects/{project_id}/subscribers/{subscriber_id}")
    assert get_response.status_code == 404
