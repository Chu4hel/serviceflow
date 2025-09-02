"""
Корневой файл конфигурации тестов Pytest.

Этот файл используется для определения глобальных фикстур и настроек,
доступных для всех тестов в проекте.

Pytest автоматически обнаруживает и использует фикстуры из файлов
с именем `conftest.py` в директории тестов и ее поддиректориях.
"""
import pytest_asyncio
import httpx
from httpx import ASGITransport

from app.core.config import settings
from app.main import app

# Указываем pytest, где искать дополнительные фикстуры.
# Это позволяет нам декомпозировать conftest.py на более мелкие, управляемые файлы.
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.users",
]

# Устанавливаем флаг, что приложение запущено в режиме тестирования.
# Это позволяет, например, использовать отдельную тестовую базу данных.
settings.TESTING = True


@pytest_asyncio.fixture(scope="function")
async def client() -> httpx.AsyncClient:
    """
    Создает и возвращает анонимный (неаутентифицированный) HTTP-клиент
    для выполнения запросов к API в тестах.
    """
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
