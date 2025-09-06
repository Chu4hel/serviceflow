"""
Сервисный слой для управления бронированиями.
"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app import schemas
from app.crud import crud_booking, crud_service
from app.services.project_service import ProjectService


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)

    async def get_booking_for_user(
            self, booking_id: int, project_id: int, current_user: models.User
    ) -> Optional[models.Booking]:
        """Получает бронирование по ID, проверяя права доступа и принадлежность к проекту."""
        project = await self.project_service.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return None

        booking = await crud_booking.get_booking(self.db, booking_id=booking_id)
        if not booking or booking.project_id != project.id:
            return None

        return booking

    async def get_bookings_for_user(
            self, project_id: int, current_user: models.User, skip: int, limit: int
    ) -> Optional[List[models.Booking]]:
        """Получает список бронирований для проекта, проверяя права доступа."""
        project = await self.project_service.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return None
        return await crud_booking.get_bookings(self.db, project_id=project_id, skip=skip, limit=limit)

    async def create_public_booking(
            self, project_id: int, booking_in: schemas.BookingCreate, allow_duplicates: bool = False
    ) -> models.Booking:
        """Создает бронирование от имени публичного пользователя (через API-ключ)."""
        if not allow_duplicates:
            existing_booking = await crud_booking.get_booking_by_service_and_time(
                self.db, project_id=project_id, service_id=booking_in.service_id, booking_time=booking_in.booking_time
            )
            if existing_booking:
                return existing_booking
        return await crud_booking.create_booking(self.db, project_id=project_id, booking=booking_in)

    async def update_booking_for_user(
            self, booking_id: int, project_id: int, booking_in: schemas.BookingUpdate, current_user: models.User
    ) -> Optional[models.Booking]:
        """Обновляет бронирование, проверяя права доступа."""
        booking = await self.get_booking_for_user(booking_id=booking_id, project_id=project_id,
                                                  current_user=current_user)
        if not booking:
            return None

        # Проверяем, что если service_id меняется, то новая услуга принадлежит тому же проекту
        update_data = booking_in.model_dump(exclude_unset=True)
        if "service_id" in update_data:
            new_service_id = update_data["service_id"]
            service = await crud_service.get_service(self.db, service_id=new_service_id)
            if not service or service.project_id != booking.project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Услуга с ID {new_service_id} не найдена или не принадлежит проекту {booking.project_id}."
                )

        return await crud_booking.update_booking(self.db, db_obj=booking, obj_in=booking_in)

    async def delete_booking_for_user(self, booking_id: int, project_id: int, current_user: models.User) -> bool:
        """Удаляет бронирование, проверяя права доступа."""
        booking = await self.get_booking_for_user(booking_id=booking_id, project_id=project_id,
                                                  current_user=current_user)
        if not booking:
            return False
        await crud_booking.delete_booking(self.db, db_obj=booking)
        return True
