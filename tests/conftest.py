"""
Настройки и фикстуры для тестов Pytest.
"""
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, get_db
from app.main import app
from app.models import serviceflow as models

# Устанавливаем флаг тестирования
settings.TESTING = True


@pytest.fixture(scope="session")
def test_user_data() -> dict:
    return {"name": "Test User", "email": "test@example.com", "password": "password"}


@pytest.fixture(scope="session")
def second_user_data() -> dict:
    return {"name": "Second User", "email": "test2@example.com", "password": "password2"}


@pytest.fixture(scope="session")
def superuser_data() -> dict:
    return {"name": "Super User", "email": "super@example.com", "password": "superpassword"}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Создает и удаляет саму тестовую базу данных один раз за сессию.
    """
    default_db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    engine = create_async_engine(default_db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {settings.TEST_POSTGRES_DB} WITH (FORCE)"))
        await conn.execute(text(f"CREATE DATABASE {settings.TEST_POSTGRES_DB}"))
    await engine.dispose()

    yield

    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {settings.TEST_POSTGRES_DB} WITH (FORCE)"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Для КАЖДОГО теста:
    1. Создает новый движок и таблицы.
    2. Создает сессию и переопределяет зависимость get_db.
    3. После теста удаляет таблицы и закрывает движок.
    """
    test_db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.TEST_POSTGRES_DB}"
    engine = create_async_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with TestingSessionLocal() as session:
        yield session

    # Очистка
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
    del app.dependency_overrides[get_db]


@pytest_asyncio.fixture(scope="function")
async def client() -> httpx.AsyncClient:
    """
    Создает анонимный HTTP-клиент для тестирования API.
    """
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


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


@pytest_asyncio.fixture(scope="function")
async def second_user_auth_client(
        client: AsyncClient, second_user: models.User, second_user_data: dict
) -> httpx.AsyncClient:
    """Возвращает клиент, аутентифицированный как второй обычный пользователь."""
    # Нужен новый инстанс клиента, чтобы заголовки не пересекались
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as new_client:
        yield await get_auth_client(new_client, second_user_data)
