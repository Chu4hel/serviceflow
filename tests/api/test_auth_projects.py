"""Тесты авторизации для эндпоинтов Проектов (/manage/projects)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


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