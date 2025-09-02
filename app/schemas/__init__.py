"""
Этот файл превращает директорию `schemas` в пакет Python
и собирает все схемы из отдельных модулей в единое пространство имен.

Это позволяет импортировать любую схему через `from app import schemas`,
сохраняя при этом код схем в отдельных, логически сгруппированных файлах.
"""

from .user import User, UserCreate, UserUpdate
from .service import Service, ServiceCreate, ServiceUpdate
from .booking import Booking, BookingCreate, BookingUpdate
from .subscriber import Subscriber, SubscriberCreate
from .project import Project, ProjectCreate, ProjectUpdate
