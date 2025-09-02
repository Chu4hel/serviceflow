"""
CRUD-операции для модели Project.
"""
from typing import List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_project(db: AsyncSession, project_id: int) -> Optional[models.Project]:
    result = await db.execute(
        select(models.Project)
        .options(
            selectinload(models.Project.user),
            selectinload(models.Project.services),
            selectinload(models.Project.bookings),
            selectinload(models.Project.subscribers)
        )
        .where(models.Project.id == project_id)
    )
    return result.scalars().first()


async def get_project_by_name_and_user(db: AsyncSession, user_id: int, name: str) -> Optional[models.Project]:
    result = await db.execute(
        select(models.Project).where(models.Project.user_id == user_id, models.Project.name == name)
    )
    return result.scalars().first()


async def get_project_by_apikey(db: AsyncSession, api_key: str) -> Optional[models.Project]:
    result = await db.execute(
        select(models.Project).where(models.Project.api_key == api_key)
    )
    return result.scalars().first()


async def get_projects_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Project]:
    result = await db.execute(
        select(models.Project)
        .where(models.Project.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
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
