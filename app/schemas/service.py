"""Pydantic схемы для Услуги (Service)."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price: Decimal


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[Decimal] = None


class Service(ServiceBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
