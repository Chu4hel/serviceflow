"""
CRUD-операции для модели Service.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_service(db: AsyncSession, service_id: int) -> Optional[models.Service]:
    result = await db.execute(
        select(models.Service)
        .options(
            selectinload(models.Service.project),
            selectinload(models.Service.bookings)
        )
        .where(models.Service.id == service_id)
    )
    return result.scalars().first()


async def get_service_by_name_and_project(db: AsyncSession, project_id: int, name: str) -> Optional[models.Service]:
    result = await db.execute(
        select(models.Service).where(models.Service.project_id == project_id, models.Service.name == name)
    )
    return result.scalars().first()


async def get_services(db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100) -> List[models.Service]:
    result = await db.execute(
        select(models.Service)
        .where(models.Service.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_service(db: AsyncSession, project_id: int, service: schemas.ServiceCreate) -> models.Service:
    db_service = models.Service(
        **service.model_dump(),
        project_id=project_id
    )
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service
