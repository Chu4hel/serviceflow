"""
CRUD-операции для модели Project.

Эти функции выполняют только базовые операции с базой данных (создание, чтение,
обновление, удаление) и не содержат никакой бизнес-логики или проверок прав доступа.
"""
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models
from app import schemas


async def get_project(db: AsyncSession, project_id: int) -> Optional[models.Project]:
    """Получает проект по ID со всеми связанными данными."""
    query = select(models.Project).options(
        selectinload(models.Project.user),
        selectinload(models.Project.services),
        selectinload(models.Project.bookings),
        selectinload(models.Project.subscribers)
    ).where(models.Project.id == project_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_project_by_name(
        db: AsyncSession, name: str, user_id: Optional[int] = None
) -> Optional[models.Project]:
    """Получает проект по имени. Если указан user_id, ищет только среди проектов этого пользователя."""
    query = select(models.Project).where(models.Project.name == name)
    if user_id:
        query = query.where(models.Project.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_project_by_apikey(db: AsyncSession, api_key: str) -> Optional[models.Project]:
    """Получает проект по его API-ключу."""
    result = await db.execute(
        select(models.Project).where(models.Project.api_key == api_key)
    )
    return result.scalars().first()


async def get_projects(
        db: AsyncSession, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.Project]:
    """Получает список проектов. Если указан user_id, возвращает проекты только этого пользователя."""
    query = select(models.Project).options(
        selectinload(models.Project.user),
        selectinload(models.Project.services),
        selectinload(models.Project.bookings),
        selectinload(models.Project.subscribers)
    )
    if user_id:
        query = query.where(models.Project.user_id == user_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_project(db: AsyncSession, user_id: int, project_in: schemas.ProjectCreate) -> models.Project:
    """Создает новый проект для указанного пользователя."""
    api_key = str(uuid.uuid4())
    db_project = models.Project(
        **project_in.model_dump(),
        user_id=user_id,
        api_key=api_key
    )
    db.add(db_project)
    await db.commit()

    # Повторно извлекаем объект для загрузки связей
    result = await db.execute(
        select(models.Project).options(
            selectinload(models.Project.user),
            selectinload(models.Project.services),
            selectinload(models.Project.bookings),
            selectinload(models.Project.subscribers)
        ).where(models.Project.id == db_project.id)
    )
    return result.scalars().first()


async def update_project(
        db: AsyncSession, db_obj: models.Project, obj_in: schemas.ProjectUpdate
) -> models.Project:
    """Обновляет данные проекта в базе данных."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    # Повторно извлекаем объект, чтобы гарантированно получить свежие данные
    return await get_project(db, project_id=db_obj.id)


async def delete_project(db: AsyncSession, db_obj: models.Project):
    """Удаляет проект из базы данных."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj
