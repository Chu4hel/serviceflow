"""
CRUD-операции для модели Project.
"""
from typing import List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models
from app import schemas


async def get_project(
        db: AsyncSession, project_id: int, current_user: models.User
) -> Optional[models.Project]:
    """
    Получает проект по ID с проверкой прав доступа.
    Суперпользователь может получить любой проект.
    Обычный пользователь - только свой.
    """
    query = select(models.Project).options(
        selectinload(models.Project.user),
        selectinload(models.Project.services),
        selectinload(models.Project.bookings),
        selectinload(models.Project.subscribers)
    ).where(models.Project.id == project_id)

    if not current_user.is_superuser:
        query = query.where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_project_by_name(
        db: AsyncSession, name: str, current_user: models.User
) -> Optional[models.Project]:
    """
    Получает проект по имени с учетом текущего пользователя.
    Суперпользователь может искать среди всех проектов.
    Обычный пользователь - только среди своих.
    """
    query = select(models.Project).where(models.Project.name == name)
    if not current_user.is_superuser:
        query = query.where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_project_by_apikey(db: AsyncSession, api_key: str) -> Optional[models.Project]:
    result = await db.execute(
        select(models.Project).where(models.Project.api_key == api_key)
    )
    return result.scalars().first()


async def get_projects(
        db: AsyncSession, current_user: models.User, skip: int = 0, limit: int = 100
) -> List[models.Project]:
    """
    Получает список проектов с учетом прав доступа.
    Суперпользователь получает все проекты.
    Обычный пользователь - только свои.
    """
    query = select(models.Project).options(
        selectinload(models.Project.user),
        selectinload(models.Project.services),
        selectinload(models.Project.bookings),
        selectinload(models.Project.subscribers)
    )

    if not current_user.is_superuser:
        query = query.where(models.Project.user_id == current_user.id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_project(db: AsyncSession, user_id: int, project_in: schemas.ProjectCreate) -> models.Project:
    api_key = str(uuid.uuid4())
    db_project = models.Project(
        **project_in.model_dump(),
        user_id=user_id,
        api_key=api_key
    )
    db.add(db_project)
    await db.commit()

    # Повторно извлекаем объект с "жадной" загрузкой всех необходимых связей
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
    """Обновляет проект в базе данных."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_project(db: AsyncSession, db_obj: models.Project):
    """Удаляет проект из базы данных."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj
