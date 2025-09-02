"""Фикстуры для настройки тестовой базы данных."""
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app


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
