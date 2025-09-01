"""
Pydantic схемы для проекта ServiceFlow.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# ==============================================================================
# Схемы для Пользователя (User)
# ==============================================================================

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Схемы для Услуги (Service)
# ==============================================================================

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price: Decimal

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Схемы для Бронирования (Booking)
# ==============================================================================

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

class Booking(BookingBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    service: Service # Вложенная схема для деталей услуги
    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Схемы для Подписчика (Subscriber)
# ==============================================================================

class SubscriberBase(BaseModel):
    email: str

class SubscriberCreate(SubscriberBase):
    pass

class Subscriber(SubscriberBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Схемы для Проекта (Project)
# ==============================================================================

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    model_config = ConfigDict(from_attributes=True, title="Проект (модель ответа)")
    id: int
    user_id: int
    api_key: str
    created_at: datetime
    updated_at: datetime
    user: User # Вложенная схема для деталей пользователя
    services: List[Service] = []
    bookings: List[Booking] = []
    subscribers: List[Subscriber] = []
    model_config = ConfigDict(from_attributes=True)

# Обновляем ссылки для вложенных схем, которые ссылаются друг на друга
# Это нужно, если есть циклические зависимости
Booking.model_rebuild()
Project.model_rebuild()
