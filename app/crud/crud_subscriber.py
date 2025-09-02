"""
CRUD-операции для модели Subscriber.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_subscriber(
        db: AsyncSession, subscriber_id: int, current_user: models.User
) -> Optional[models.Subscriber]:
    """
    Получает подписчика по ID с проверкой прав доступа.
    """
    query = select(models.Subscriber).where(models.Subscriber.id == subscriber_id)

    if not current_user.is_superuser:
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_subscriber_by_email_and_project(
        db: AsyncSession, project_id: int, email: str, current_user: Optional[models.User] = None
) -> Optional[models.Subscriber]:
    """
    Ищет подписчика по email и ID проекта.
    Если передан current_user, проверяет права доступа.
    """
    query = select(models.Subscriber).where(
        models.Subscriber.project_id == project_id, models.Subscriber.email == email
    )

    if current_user and not current_user.is_superuser:
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    result = await db.execute(query)
    return result.scalars().first()


async def get_subscribers(
        db: AsyncSession, project_id: int, current_user: models.User, skip: int = 0, limit: int = 100
) -> List[models.Subscriber]:
    """
    Получает список подписчиков для проекта с проверкой прав.
    """
    query = select(models.Subscriber).where(models.Subscriber.project_id == project_id)

    if not current_user.is_superuser:
        query = query.join(models.Project).where(models.Project.user_id == current_user.id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_subscriber(
        db: AsyncSession, project_id: int, subscriber: schemas.SubscriberCreate
) -> models.Subscriber:
    """
    Создает нового подписчика.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте): Убедиться, что current_user имеет доступ к project_id.
    """
    db_subscriber = models.Subscriber(
        **subscriber.model_dump(),
        project_id=project_id
    )
    db.add(db_subscriber)
    await db.commit()
    await db.refresh(db_subscriber)
    return db_subscriber


async def delete_subscriber(db: AsyncSession, db_obj: models.Subscriber):
    """
    Удаляет подписчика из базы данных.
    ПРЕДУСЛОВИE (выполняется в эндпоинте): db_obj получен через get_subscriber с проверкой прав.
    """
    await db.delete(db_obj)
    await db.commit()
    return db_obj
