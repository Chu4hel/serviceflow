"""Тесты авторизации для эндпоинтов Услуг (/manage/projects/{project_id}/services)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


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