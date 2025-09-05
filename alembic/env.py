import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Импортируем наши настройки и базовую модель
from app.core.config import settings
from app.db.session import Base  # Убедитесь, что все модели импортированы через Base

config = context.config

# Настраиваем логирование из ini-файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные моделей для поддержки автогенерации
target_metadata = Base.metadata

# Получаем URL для подключения к БД из настроек приложения
async_db_url = settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'."""
    context.configure(
        url=str(async_db_url),  # Используем наш URL
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'.

    Для этого режима необходимо создать движок (Engine)
    и связать соединение с текущим контекстом.
    """
    # Создаем асинхронный движок из нашего URL
    connectable = create_async_engine(str(async_db_url), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
