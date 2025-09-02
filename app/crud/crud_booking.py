"""
CRUD-операции для модели Booking.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import serviceflow as models
from app.schemas import serviceflow as schemas


async def get_booking(db: AsyncSession, booking_id: int) -> Optional[models.Booking]:
    """Получить бронирование по ID с подгрузкой связанных услуг."""
    result = await db.execute(
        select(models.Booking)
        .options(selectinload(models.Booking.service))
        .where(models.Booking.id == booking_id)
    )
    return result.scalars().first()


async def get_booking_by_service_and_time(
        db: AsyncSession, project_id: int, service_id: int, booking_time: datetime
) -> Optional[models.Booking]:
    """Ищет бронирование по ID сервиса и времени в рамках одного проекта."""
    result = await db.execute(
        select(models.Booking).where(
            models.Booking.project_id == project_id,
            models.Booking.service_id == service_id,
            models.Booking.booking_time == booking_time
        )
    )
    return result.scalars().first()


async def get_bookings(db: AsyncSession, project_id: int, skip: int = 0, limit: int = 100) -> List[models.Booking]:
    """Получить список бронирований для конкретного проекта."""
    result = await db.execute(
        select(models.Booking)
        .where(models.Booking.project_id == project_id)
        .options(selectinload(models.Booking.service))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_booking(db: AsyncSession, project_id: int, booking: schemas.BookingCreate) -> models.Booking:
    """Создать новое бронирование для проекта."""
    db_booking = models.Booking(
        **booking.model_dump(),
        project_id=project_id
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking, ["service"])  # Обновляем, чтобы подгрузить связь
    return db_booking
