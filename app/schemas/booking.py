"""Pydantic схемы для Бронирования (Booking)."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from .service import Service


class BookingBase(BaseModel):
    service_id: int
    booking_time: datetime
    client_name: str
    client_email: Optional[str] = None
    client_phone: str
    status: str = 'new'
    description: Optional[str] = None
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    booking_time: Optional[datetime] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class Booking(BookingBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    service: Service  # Вложенная схема для деталей услуги
    model_config = ConfigDict(from_attributes=True)


Booking.model_rebuild()
