"""
CRUD-операции для модели User.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.security import get_password_hash
from app import models
from app import schemas


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """
    Получает пользователя по ID.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    - Суперпользователь может получить любого пользователя.
    - Обычный пользователь может получить только самого себя (current_user.id == user_id).
    """
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def get_users(
        db: AsyncSession, current_user: models.User, skip: int = 0, limit: int = 100
) -> List[models.User]:
    """
    Возвращает список пользователей. Доступно только для суперпользователей.
    """
    if not current_user.is_superuser:
        return []
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """
    Создает нового пользователя.
    ПРИМЕЧАНИЕ: Логика, кто может создавать пользователя (все, только
    суперпользователи?), должна быть реализована в эндпоинте.
    """
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


async def update_user(
        db: AsyncSession, db_obj: models.User, obj_in: schemas.UserUpdate
) -> models.User:
    """
    Обновляет пользователя в базе данных.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    - Суперпользователь может обновлять любого пользователя.
    - Обычный пользователь может обновлять только самого себя.
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]  # Удаляем, чтобы не записать открытый пароль
        setattr(db_obj, "hashed_password", hashed_password)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_user(db: AsyncSession, db_obj: models.User):
    """

    Удаляет пользователя из базы данных.
    ПРЕДУСЛОВИЕ (выполняется в эндпоинте):
    - Суперпользователь может удалять любого пользователя.
    - Обычный пользователь может удалять только самого себя.
    """
    await db.delete(db_obj)
    await db.commit()
    return db_obj
