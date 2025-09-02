"""
Management API: Эндпоинты для управления бронированиями.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.services.booking_service import BookingService
from app.db.session import get_db
from app import models
from app import schemas

router = APIRouter()


@router.get("/projects/{project_id}/bookings", response_model=List[schemas.Booking],
            summary="Получение списка бронирований проекта")
async def read_project_bookings(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    booking_service = BookingService(db)
    bookings = await booking_service.get_bookings_for_user(
        project_id=project_id, current_user=current_user, skip=skip, limit=limit
    )
    if bookings is None:
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")
    return bookings


@router.get("/projects/{project_id}/bookings/{booking_id}", response_model=schemas.Booking,
            summary="Получение бронирования по ID")
async def read_project_booking(
        project_id: int,
        booking_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    booking_service = BookingService(db)
    booking = await booking_service.get_booking_for_user(
        booking_id=booking_id, project_id=project_id, current_user=current_user
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или не принадлежит указанному проекту")
    return booking


@router.put("/projects/{project_id}/bookings/{booking_id}", response_model=schemas.Booking,
            summary="Обновление бронирования")
async def update_project_booking(
        project_id: int,
        booking_id: int,
        booking_in: schemas.BookingUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    booking_service = BookingService(db)
    booking = await booking_service.update_booking_for_user(
        booking_id=booking_id, project_id=project_id, booking_in=booking_in, current_user=current_user
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или не принадлежит указанному проекту")
    return booking


@router.delete("/projects/{project_id}/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удаление бронирования")
async def delete_project_booking(
        project_id: int,
        booking_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    booking_service = BookingService(db)
    success = await booking_service.delete_booking_for_user(
        booking_id=booking_id, project_id=project_id, current_user=current_user
    )
    if not success:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или не принадлежит указанному проекту")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
