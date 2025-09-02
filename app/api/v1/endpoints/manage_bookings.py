"""
Management API: Эндпоинты для управления бронированиями.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.crud import crud_booking, crud_project
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
    # crud_booking.get_bookings теперь сам проверяет права доступа
    bookings = await crud_booking.get_bookings(
        db, project_id=project_id, current_user=current_user, skip=skip, limit=limit
    )
    # Дополнительная проверка, на случай если проекта не существует
    if not bookings:
        project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
        if not project:
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
    booking = await crud_booking.get_booking(db, booking_id=booking_id, current_user=current_user)
    if not booking or booking.project_id != project_id:
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
    booking = await crud_booking.get_booking(db, booking_id=booking_id, current_user=current_user)
    if not booking or booking.project_id != project_id:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или не принадлежит указанному проекту")

    updated_booking = await crud_booking.update_booking(db=db, db_obj=booking, obj_in=booking_in)
    return updated_booking


@router.delete("/projects/{project_id}/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удаление бронирования")
async def delete_project_booking(
        project_id: int,
        booking_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    booking = await crud_booking.get_booking(db, booking_id=booking_id, current_user=current_user)
    if not booking or booking.project_id != project_id:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или не принадлежит указанному проекту")

    await crud_booking.delete_booking(db=db, db_obj=booking)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
