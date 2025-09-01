"""
Public API: Эндпоинты для работы с бронированиями (создание).
Требуют X-API-KEY.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_project_by_api_key
from app.crud import crud_booking
from app.db.session import get_db
from app.models.serviceflow import Project
from app.schemas import serviceflow as schemas

router = APIRouter()

@router.post("/bookings", response_model=schemas.Booking, status_code=201)
async def create_public_booking(
    booking: schemas.BookingCreate,
    project: Project = Depends(get_project_by_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await crud_booking.create_booking(db=db, project_id=project.id, booking=booking)
