"""
CRUD-операции для модели Subscriber.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_subscriber(db: AsyncSession, subscriber_id: int) -> Optional[models.Subscriber]:
    result = await db.execute(
        select(models.Subscriber).where(models.Subscriber.id == subscriber_id)
    )
    return result.scalars().first()


async def get_subscribers(db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100) -> List[models.Subscriber]:
    result = await db.execute(
        select(models.Subscriber)
        .where(models.Subscriber.project_id == project_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_subscriber(db: AsyncSession, project_id: int, subscriber: schemas.SubscriberCreate) -> models.Subscriber:
    db_subscriber = models.Subscriber(
        **subscriber.model_dump(),
        project_id=project_id
    )
    db.add(db_subscriber)
    await db.commit()
    await db.refresh(db_subscriber)
    return db_subscriber
