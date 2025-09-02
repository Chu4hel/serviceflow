"""Фикстуры для создания пользователей и аутентифицированных клиентов."""
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.main import app
from app import models


@pytest.fixture(scope="session")
def test_user_data() -> dict:
    return {"name": "Test User", "email": "test@example.com", "password": "password"}


@pytest.fixture(scope="session")
def second_user_data() -> dict:
    return {"name": "Second User", "email": "test2@example.com", "password": "password2"}


@pytest.fixture(scope="session")
def superuser_data() -> dict:
    return {"name": "Super User", "email": "super@example.com", "password": "superpassword"}


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession, test_user_data: dict) -> models.User:
    """Создает и возвращает обычного пользователя."""
    user = models.User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def superuser(db_session: AsyncSession, superuser_data: dict) -> models.User:
    """Создает и возвращает суперпользователя."""
    user = models.User(
        name=superuser_data["name"],
        email=superuser_data["email"],
        hashed_password=get_password_hash(superuser_data["password"]),
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def second_user(db_session: AsyncSession, second_user_data: dict) -> models.User:
    """Создает и возвращает второго обычного пользователя."""
    user = models.User(
        name=second_user_data["name"],
        email=second_user_data["email"],
        hashed_password=get_password_hash(second_user_data["password"]),
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def get_auth_client(client: AsyncClient, user_data: dict) -> httpx.AsyncClient:
    """Вспомогательная функция для получения аутентифицированного клиента."""
    login_response = await client.post(
        "/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture(scope="function")
async def test_user_auth_client(
        test_user: models.User, test_user_data: dict
) -> httpx.AsyncClient:
    """Возвращает клиент, аутентифицированный как обычный пользователь."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield await get_auth_client(client, test_user_data)


@pytest_asyncio.fixture(scope="function")
async def superuser_auth_client(
        superuser: models.User, superuser_data: dict
) -> httpx.AsyncClient:
    """Возвращает клиент, аутентифицированный как суперпользователь."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield await get_auth_client(client, superuser_data)


@pytest_asyncio.fixture(scope="function")
async def second_user_auth_client(
        client: AsyncClient, second_user: models.User, second_user_data: dict
) -> httpx.AsyncClient:
    """Возвращает клиент, аутентифицированный как второй обычный пользователь."""
    # Нужен новый инстанс клиента, чтобы заголовки не пересекались
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as new_client:
        yield await get_auth_client(new_client, second_user_data)
