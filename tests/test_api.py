"""
Автоматические тесты для API ServiceFlow.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user, crud_project, crud_service
from app.schemas import serviceflow as schemas

pytestmark = pytest.mark.asyncio


async def create_user_and_get_token(client: AsyncClient, db_session: AsyncSession, user_data: dict):
    """Вспомогательная функция для создания пользователя и получения токена."""
    await client.post("/manage/users", json=user_data)
    login_response = await client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    return login_response.json()["access_token"]


async def create_project(client: AsyncClient, token: str, project_data: dict):
    """Вспомогательная функция для создания проекта."""
    response = await client.post(
        "/manage/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# ==============================================================================
# Тесты для Услуг (Services)
# ==============================================================================

async def test_create_service_no_duplicates(client: AsyncClient, db_session: AsyncSession):
    """Тест: нельзя создать дубликат услуги по умолчанию."""
    # 1. Создаем пользователя и проект
    user_data = {"name": "test_user_service", "email": "test_user_service@example.com", "password": "password"}
    token = await create_user_and_get_token(client, db_session, user_data)
    project = await create_project(client, token, {"name": "Test Project for Services"})
    project_id = project["id"]

    # 2. Создаем услугу
    service_data = {"name": "Cleaning", "duration_minutes": 60, "price": 50.00}
    response1 = await client.post(
        f"/manage/projects/{project_id}/services",
        json=service_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 201
    created_service = response1.json()
    assert created_service["name"] == service_data["name"]

    # 3. Пытаемся создать ту же услугу еще раз (allow_duplicates=False)
    response2 = await client.post(
        f"/manage/projects/{project_id}/services",
        json=service_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200 # Ожидаем 200 OK
    existing_service = response2.json()
    assert existing_service["id"] == created_service["id"]
    assert existing_service["name"] == service_data["name"]

async def test_create_service_with_duplicates_allowed(client: AsyncClient, db_session: AsyncSession):
    """Тест: можно создать дубликат услуги с флагом allow_duplicates=True."""
    # 1. Создаем пользователя и проект
    user_data = {"name": "test_user_service_dup", "email": "test_user_service_dup@example.com", "password": "password"}
    token = await create_user_and_get_token(client, db_session, user_data)
    project = await create_project(client, token, {"name": "Test Project for Service Duplicates"})
    project_id = project["id"]

    # 2. Создаем услугу
    service_data = {"name": "Gardening", "duration_minutes": 120, "price": 75.00}
    response1 = await client.post(
        f"/manage/projects/{project_id}/services",
        json=service_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 201
    created_service_1 = response1.json()

    # 3. Создаем дубликат с allow_duplicates=True
    response2 = await client.post(
        f"/manage/projects/{project_id}/services?allow_duplicates=True",
        json=service_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 201 # Ожидаем 201 Created
    created_service_2 = response2.json()
    assert created_service_2["id"] != created_service_1["id"]
    assert created_service_2["name"] == service_data["name"]


# ==============================================================================
# Тесты для Бронирований (Bookings)
# ==============================================================================

async def test_create_booking_no_duplicates(client: AsyncClient, db_session: AsyncSession):
    """Тест: нельзя создать дубликат бронирования по умолчанию."""
    # 1. Создаем пользователя, проект и услугу
    user_data = {"name": "test_user_booking", "email": "test_user_booking@example.com", "password": "password"}
    token = await create_user_and_get_token(client, db_session, user_data)
    project = await create_project(client, token, {"name": "Test Project for Bookings"})
    project_id = project["id"]
    api_key = project["api_key"]
    service_data = {"name": "Plumbing", "duration_minutes": 45, "price": 99.99}
    service_response = await client.post(
        f"/manage/projects/{project_id}/services", json=service_data, headers={"Authorization": f"Bearer {token}"}
    )
    service_id = service_response.json()["id"]

    # 2. Создаем бронирование
    booking_data = {
        "service_id": service_id,
        "booking_time": "2025-09-15T10:00:00",
        "client_name": "John Doe",
        "client_phone": "+1234567890"
    }
    response1 = await client.post(
        "/public/v1/bookings",
        json=booking_data,
        headers={"X-API-KEY": api_key}
    )
    assert response1.status_code == 201
    created_booking = response1.json()

    # 3. Пытаемся создать дубликат
    response2 = await client.post(
        "/public/v1/bookings",
        json=booking_data,
        headers={"X-API-KEY": api_key}
    )
    assert response2.status_code == 200
    existing_booking = response2.json()
    assert existing_booking["id"] == created_booking["id"]

async def test_create_booking_with_duplicates_allowed(client: AsyncClient, db_session: AsyncSession):
    """Тест: можно создать дубликат бронирования с флагом allow_duplicates=True."""
    # 1. Создаем пользователя, проект и услугу
    user_data = {"name": "test_user_booking_dup", "email": "test_user_booking_dup@example.com", "password": "password"}
    token = await create_user_and_get_token(client, db_session, user_data)
    project = await create_project(client, token, {"name": "Test Project for Booking Duplicates"})
    project_id = project["id"]
    api_key = project["api_key"]
    service_data = {"name": "Electrical", "duration_minutes": 90, "price": 150.00}
    service_response = await client.post(
        f"/manage/projects/{project_id}/services", json=service_data, headers={"Authorization": f"Bearer {token}"}
    )
    service_id = service_response.json()["id"]

    # 2. Создаем бронирование
    booking_data = {
        "service_id": service_id,
        "booking_time": "2025-09-16T14:00:00",
        "client_name": "Jane Smith",
        "client_phone": "+0987654321"
    }
    response1 = await client.post(
        "/public/v1/bookings", json=booking_data, headers={"X-API-KEY": api_key}
    )
    assert response1.status_code == 201
    created_booking_1 = response1.json()

    # 3. Создаем дубликат с allow_duplicates=True
    response2 = await client.post(
        "/public/v1/bookings?allow_duplicates=True",
        json=booking_data,
        headers={"X-API-KEY": api_key}
    )
    assert response2.status_code == 201
    created_booking_2 = response2.json()
    assert created_booking_2["id"] != created_booking_1["id"]


# ==============================================================================
# Тесты для Подписчиков (Subscribers)
# ==============================================================================

async def test_create_subscriber_handles_duplicates(client: AsyncClient, db_session: AsyncSession):
    """Тест: эндпоинт создания подписчика корректно обрабатывает дубликаты."""
    # 1. Создаем пользователя и проект
    user_data = {"name": "test_user_sub", "email": "test_user_sub@example.com", "password": "password"}
    token = await create_user_and_get_token(client, db_session, user_data)
    project = await create_project(client, token, {"name": "Test Project for Subscribers"})
    api_key = project["api_key"]

    # 2. Создаем подписчика
    subscriber_data = {"email": "subscriber1@example.com"}
    response1 = await client.post(
        "/public/v1/subscribers",
        json=subscriber_data,
        headers={"X-API-KEY": api_key}
    )
    assert response1.status_code == 201
    created_subscriber = response1.json()

    # 3. Пытаемся создать дубликат
    response2 = await client.post(
        "/public/v1/subscribers",
        json=subscriber_data,
        headers={"X-API-KEY": api_key}
    )
    assert response2.status_code == 200
    existing_subscriber = response2.json()
    assert existing_subscriber["id"] == created_subscriber["id"]
