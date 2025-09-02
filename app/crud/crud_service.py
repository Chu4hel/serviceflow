"""
CRUD-операции для модели Service.

Эти функции выполняют только базовые операции с базой данных и не содержат
бизнес-логики или проверок прав доступа.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models
from app import schemas


async def get_service(db: AsyncSession, service_id: int) -> Optional[models.Service]:
    """Получает услугу по ID."""
    query = select(models.Service).options(
        selectinload(models.Service.project),
        selectinload(models.Service.bookings)
    ).where(models.Service.id == service_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_service_by_name_and_project(
        db: AsyncSession, project_id: int, name: str
) -> Optional[models.Service]:
    """Получает услугу по имени и ID проекта."""
    query = select(models.Service).where(
        models.Service.project_id == project_id,
        models.Service.name == name
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_services(
        db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100
) -> List[models.Service]:
    """Получает список услуг для проекта."""
    query = select(models.Service)
    if project_id:
        query = query.where(models.Service.project_id == project_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_service(db: AsyncSession, project_id: int, service: schemas.ServiceCreate) -> models.Service:
    """Создает новую услугу в проекте."""
    db_service = models.Service(
        **service.model_dump(),
        project_id=project_id
    )
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)
    return db_service


async def update_service(
        db: AsyncSession, db_obj: models.Service, obj_in: schemas.ServiceUpdate
) -> models.Service:
    """Обновляет данные услуги."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_service(db: AsyncSession, db_obj: models.Service):
    """Удаляет услугу."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj