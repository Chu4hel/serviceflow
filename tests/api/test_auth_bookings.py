"""Тесты авторизации для эндпоинтов Бронирований (/manage/projects/{project_id}/bookings)."""
import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def user_booking(client: AsyncClient, user_project: dict, user_service: dict) -> dict:
    """Создает бронирование через публичный API."""
    api_key = user_project["api_key"]
    booking_data = {
        "service_id": user_service["id"],
        "booking_time": "2025-10-01T10:00:00",
        "client_name": "Test Client",
        "client_phone": "12345"
    }
    response = await client.post("/public/v1/bookings", json=booking_data, headers={"X-API-KEY": api_key})
    assert response.status_code == 201
    return response.json()


async def test_user_can_get_own_booking(test_user_auth_client: AsyncClient, user_project: dict, user_booking: dict):
    """Пользователь может получить свое бронирование."""
    project_id = user_project["id"]
    booking_id = user_booking["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


async def test_user_cannot_get_booking_from_other_project(test_user_auth_client: AsyncClient, superuser_project: dict,
                                                          user_booking: dict):
    """Пользователь не может получить бронирование из чужого проекта."""
    project_id = superuser_project["id"]
    booking_id = user_booking["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}/bookings/{booking_id}")
    assert response.status_code == 404
