"""
CRUD-операции для модели Booking.

Эти функции выполняют только базовые операции с базой данных и не содержат
бизнес-логики или проверок прав доступа.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import models
from app import schemas


async def get_booking(db: AsyncSession, booking_id: int) -> Optional[models.Booking]:
    """Получает бронирование по ID."""
    query = select(models.Booking).options(
        selectinload(models.Booking.service)
    ).where(models.Booking.id == booking_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_booking_by_service_and_time(
        db: AsyncSession, project_id: int, service_id: int, booking_time: datetime
) -> Optional[models.Booking]:
    """Ищет бронирование по ID сервиса и времени в рамках одного проекта."""
    query = select(models.Booking).where(
        models.Booking.project_id == project_id,
        models.Booking.service_id == service_id,
        models.Booking.booking_time == booking_time
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_bookings(
        db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100
) -> List[models.Booking]:
    """Получает список бронирований для проекта."""
    query = select(models.Booking).where(models.Booking.project_id == project_id)
    query = query.options(selectinload(models.Booking.service)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_booking(db: AsyncSession, project_id: int, booking: schemas.BookingCreate) -> models.Booking:
    """Создает новое бронирование для проекта."""
    db_booking = models.Booking(
        **booking.model_dump(),
        project_id=project_id
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking, ["service"])  # Обновляем, чтобы подгрузить связь
    return db_booking


async def update_booking(
        db: AsyncSession, db_obj: models.Booking, obj_in: schemas.BookingUpdate
) -> models.Booking:
    """Обновляет бронирование в базе данных."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_booking(db: AsyncSession, db_obj: models.Booking):
    """Удаляет бронирование из базы данных."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj