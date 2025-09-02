"""
CRUD-операции для модели User.
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.security import get_password_hash
from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    # Проверяем, есть ли уже пользователи в БД
    result = await db.execute(select(func.count()).select_from(models.User))
    user_count = result.scalar_one()

    db_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=get_password_hash(user.password),
        # Первый пользователь становится суперпользователем
        is_superuser=(user_count == 0)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
