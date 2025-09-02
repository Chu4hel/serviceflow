"""
CRUD-операции для модели Service.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_service(
        db: AsyncSession, service_id: int, current_user: models.User
) -> Optional[models.Service]:
    """
    Получает услугу по ID с проверкой прав доступа.
    Суперпользователь может получить любую услугу.
    Обычный пользователь - только услугу в рамках своего проекта.
    """
    query = select(models.Service).options(
        selectinload(models.Service.project),
        selectinload(models.Service.bookings)
    ).where(models.Service.id == service_id)

    if not current_user.is_superuser:
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_service_by_name_and_project(
        db: AsyncSession, project_id: int, name: str, current_user: models.User
) -> Optional[models.Service]:
    """
    Получает услугу по имени и ID проекта с проверкой прав доступа.
    """
    query = select(models.Service).where(
        models.Service.project_id == project_id,
        models.Service.name == name
    )

    if not current_user.is_superuser:
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_services(
        db: AsyncSession, project_id: int, current_user: models.User, skip: int = 0, limit: int = 100
) -> List[models.Service]:
    """
    Получает список услуг для проекта с проверкой прав доступа.
    """
    query = select(models.Service).where(models.Service.project_id == project_id)

    if not current_user.is_superuser:
        # Убедимся, что пользователь имеет доступ к этому project_id
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_service(db: AsyncSession, project_id: int, service: schemas.ServiceCreate) -> models.Service:
    # ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    # Перед вызовом этой функции необходимо убедиться, что current_user
    # имеет право на доступ к project_id.
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
    """
    Обновляет услугу в базе данных.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    Объект db_obj должен быть получен через get_service с проверкой прав.
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_service(db: AsyncSession, db_obj: models.Service):
    """
    Удаляет услугу из базы данных.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    Объект db_obj должен быть получен через get_service с проверкой прав.
    """
    await db.delete(db_obj)
    await db.commit()
    return db_obj
