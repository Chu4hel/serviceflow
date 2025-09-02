"""
Тесты авторизации для Management API.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models.serviceflow import User, Project

pytestmark = pytest.mark.asyncio


# ==============================================================================
# Фикстуры для проектов
# ==============================================================================

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


# ==============================================================================
# Тесты для эндпоинтов Проектов (/manage/projects)
# ==============================================================================

async def test_get_own_project(test_user_auth_client: AsyncClient, user_project: dict):
    """Обычный пользователь может получить свой проект по ID."""
    project_id = user_project["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id


async def test_user1_cannot_get_user2_project(test_user_auth_client: AsyncClient, second_user_project: dict):
    """Обычный пользователь 1 не может получить проект пользователя 2."""
    project_id = second_user_project["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}")
    assert response.status_code == 404


async def test_cannot_get_other_user_project(test_user_auth_client: AsyncClient, superuser_project: dict):
    """Обычный пользователь не может получить чужой проект по ID (проект суперюзера)."""
    project_id = superuser_project["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}")
    assert response.status_code == 404


async def test_superuser_can_get_other_user_project(superuser_auth_client: AsyncClient, user_project: dict):
    """Суперпользователь может получить чужой проект по ID."""
    project_id = user_project["id"]
    response = await superuser_auth_client.get(f"/manage/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id


async def test_get_projects_list(test_user_auth_client: AsyncClient, user_project: dict):
    """Обычный пользователь видит в списке только свои проекты."""
    response = await test_user_auth_client.get("/manage/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["id"] == user_project["id"]


async def test_superuser_get_all_projects_list(superuser_auth_client: AsyncClient, user_project: dict,
                                               superuser_project: dict):
    """Суперпользователь видит в списке все проекты."""
    response = await superuser_auth_client.get("/manage/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 2
    project_ids = {p["id"] for p in projects}
    assert user_project["id"] in project_ids
    assert superuser_project["id"] in project_ids


async def test_update_own_project(test_user_auth_client: AsyncClient, user_project: dict):
    """Обычный пользователь может обновить свой проект."""
    project_id = user_project["id"]
    new_name = "Updated Project Name"
    response = await test_user_auth_client.put(f"/manage/projects/{project_id}", json={"name": new_name})
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_cannot_update_other_user_project(test_user_auth_client: AsyncClient, superuser_project: dict):
    """Обычный пользователь не может обновить чужой проект."""
    project_id = superuser_project["id"]
    response = await test_user_auth_client.put(f"/manage/projects/{project_id}", json={"name": "hacked"})
    assert response.status_code == 404


async def test_superuser_can_update_other_user_project(superuser_auth_client: AsyncClient, user_project: dict):
    """Суперпользователь может обновить чужой проект."""
    project_id = user_project["id"]
    new_name = "Updated by Superuser"
    response = await superuser_auth_client.put(f"/manage/projects/{project_id}", json={"name": new_name})
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_delete_own_project(test_user_auth_client: AsyncClient, user_project: dict):
    """Обычный пользователь может удалить свой проект."""
    project_id = user_project["id"]
    response = await test_user_auth_client.delete(f"/manage/projects/{project_id}")
    assert response.status_code == 204
    get_response = await test_user_auth_client.get(f"/manage/projects/{project_id}")
    assert get_response.status_code == 404


async def test_cannot_delete_other_user_project(test_user_auth_client: AsyncClient, superuser_project: dict):
    """Обычный пользователь не может удалить чужой проект."""
    project_id = superuser_project["id"]
    response = await test_user_auth_client.delete(f"/manage/projects/{project_id}")
    assert response.status_code == 404


async def test_superuser_can_delete_other_user_project(superuser_auth_client: AsyncClient, user_project: dict):
    """Суперпользователь может удалить чужой проект."""
    project_id = user_project["id"]
    response = await superuser_auth_client.delete(f"/manage/projects/{project_id}")
    assert response.status_code == 204
    get_response = await superuser_auth_client.get(f"/manage/projects/{project_id}")
    assert get_response.status_code == 404


# ==============================================================================
# Тесты для эндпоинтов Услуг (/manage/projects/{project_id}/services)
# ==============================================================================

@pytest_asyncio.fixture(scope="function")
async def user_service(test_user_auth_client: AsyncClient, user_project: dict) -> dict:
    """Создает услугу в проекте обычного пользователя."""
    project_id = user_project["id"]
    service_data = {"name": "Test Service", "duration_minutes": 60, "price": 100}
    response = await test_user_auth_client.post(f"/manage/projects/{project_id}/services", json=service_data)
    assert response.status_code == 201
    return response.json()


async def test_user_can_get_own_service(test_user_auth_client: AsyncClient, user_project: dict, user_service: dict):
    """Пользователь может получить свою услугу."""
    project_id = user_project["id"]
    service_id = user_service["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}/services/{service_id}")
    assert response.status_code == 200
    assert response.json()["id"] == service_id


async def test_user_cannot_get_service_from_other_project(test_user_auth_client: AsyncClient, superuser_project: dict,
                                                          user_service: dict):
    """Пользователь не может получить услугу из чужого проекта."""
    project_id = superuser_project["id"]
    service_id = user_service["id"]
    response = await test_user_auth_client.get(f"/manage/projects/{project_id}/services/{service_id}")
    assert response.status_code == 404


async def test_superuser_can_get_any_service(superuser_auth_client: AsyncClient, user_project: dict,
                                             user_service: dict):
    """Суперпользователь может получить любую услугу."""
    project_id = user_project["id"]
    service_id = user_service["id"]
    response = await superuser_auth_client.get(f"/manage/projects/{project_id}/services/{service_id}")
    assert response.status_code == 200
    assert response.json()["id"] == service_id


async def test_user_cannot_create_service_in_other_users_project(test_user_auth_client: AsyncClient,
                                                                 superuser_project: dict):
    """Пользователь не может создать услугу в чужом проекте."""
    project_id = superuser_project["id"]
    service_data = {"name": "Hacked Service", "duration_minutes": 10, "price": 1}
    response = await test_user_auth_client.post(f"/manage/projects/{project_id}/services", json=service_data)
    assert response.status_code == 404


async def test_user_can_update_own_service(test_user_auth_client: AsyncClient, user_project: dict, user_service: dict):
    """Пользователь может обновить свою услугу."""
    project_id = user_project["id"]
    service_id = user_service["id"]
    update_data = {"name": "Updated Service Name"}
    response = await test_user_auth_client.put(f"/manage/projects/{project_id}/services/{service_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]


async def test_user_cannot_update_service_in_other_project(test_user_auth_client: AsyncClient, superuser_project: dict,
                                                           user_service: dict):
    """Пользователь не может обновить услугу в чужом проекте."""
    project_id = superuser_project["id"]
    service_id = user_service["id"]
    update_data = {"name": "Hacked"}
    response = await test_user_auth_client.put(f"/manage/projects/{project_id}/services/{service_id}", json=update_data)
    assert response.status_code == 404


async def test_superuser_can_update_any_service(superuser_auth_client: AsyncClient, user_project: dict,
                                                user_service: dict):
    """Суперпользователь может обновить любую услугу."""
    project_id = user_project["id"]
    service_id = user_service["id"]
    update_data = {"name": "Updated by Superuser"}
    response = await superuser_auth_client.put(f"/manage/projects/{project_id}/services/{service_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]


async def test_user_can_delete_own_service(test_user_auth_client: AsyncClient, user_project: dict, user_service: dict):
    """Пользователь может удалить свою услугу."""
    project_id = user_project["id"]
    service_id = user_service["id"]
    response = await test_user_auth_client.delete(f"/manage/projects/{project_id}/services/{service_id}")
    assert response.status_code == 204
    get_response = await test_user_auth_client.get(f"/manage/projects/{project_id}/services/{service_id}")
    assert get_response.status_code == 404


async def test_user_cannot_delete_service_in_other_project(test_user_auth_client: AsyncClient, superuser_project: dict,
                                                           user_service: dict):
    """Пользователь не может удалить услугу в чужом проекте."""
    project_id = superuser_project["id"]
    service_id = user_service["id"]
    response = await test_user_auth_client.delete(f"/manage/projects/{project_id}/services/{service_id}")
    assert response.status_code == 404


# ==============================================================================
# Тесты для эндпоинтов Бронирований (/manage/projects/{project_id}/bookings)
# ==============================================================================

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


# ==============================================================================
# Тесты для эндпоинтов Подписчиков (/manage/projects/{project_id}/subscribers)
# ==============================================================================

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
