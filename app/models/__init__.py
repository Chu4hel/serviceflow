"""
Этот файл превращает директорию `models` в пакет Python
и импортирует все модели SQLAlchemy из отдельных модулей.

Это позволяет другим частям приложения (например, Alembic, CRUD-операциям)
импортировать любую модель напрямую из `app.models`.
"""

from .user import User
from .project import Project
from .service import Service
from .booking import Booking
from .subscriber import Subscriber
