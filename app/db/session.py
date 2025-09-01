"""
Модуль для настройки подключения к базе данных.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Создаем асинхронный "движок"
engine = create_async_engine(str(settings.DATABASE_URL), echo=True, future=True)

# Фабрика для создания асинхронных сессий
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для всех наших SQLAlchemy моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для получения асинхронной сессии базы данных.
    """
    async with AsyncSessionLocal() as session:
        yield session
