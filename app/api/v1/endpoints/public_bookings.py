"""
Public API: Эндпоинты для работы с бронированиями (создание).
Требуют X-API-KEY.
"""
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app import schemas
from app.api.v1.dependencies import get_project_by_api_key
from app.crud import crud_booking, crud_service
from app.db.session import get_db

router = APIRouter()


@router.post(
    "/bookings",
    response_model=schemas.Booking,
    status_code=status.HTTP_201_CREATED,
    summary="Создание или получение бронирования",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Booking,
            "description": "Бронирование на эту услугу и время уже существует. Возвращены данные существующего бронирования.",
        }
    },
)
async def create_public_booking(
        booking: schemas.BookingCreate,
        project: models.Project = Depends(get_project_by_api_key),
        db: AsyncSession = Depends(get_db),
        allow_duplicates: bool = False,
):
    """
    Создает новое бронирование или возвращает существующее.

    - По умолчанию (`allow_duplicates=False`), если бронирование на указанные `service_id` и `booking_time` уже существует, возвращаются его данные со статусом 200.
    - Если бронь не найдена, она создается и возвращается со статусом 201.
    - Если `allow_duplicates=True`, система всегда создает новое бронирование.
    """
    # Универсальная обработка datetime: преобразуем aware в naive
    if booking.booking_time.tzinfo:
        booking.booking_time = booking.booking_time.replace(tzinfo=None)

    # Проверяем, что услуга принадлежит проекту
    service = await crud_service.get_service(db, service_id=booking.service_id)
    if not service or service.project_id != project.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Услуга с ID {booking.service_id} не найдена или не принадлежит данному проекту."
        )

    if not allow_duplicates:
        existing_booking = await crud_booking.get_booking_by_service_and_time(
            db, project_id=project.id, service_id=booking.service_id, booking_time=booking.booking_time
        )
        if existing_booking:
            booking_with_relations = await crud_booking.get_booking(db, booking_id=existing_booking.id)
            booking_schema = schemas.Booking.model_validate(booking_with_relations)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(booking_schema))

    return await crud_booking.create_booking(db=db, project_id=project.id, booking=booking)
