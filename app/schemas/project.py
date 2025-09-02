"""Pydantic схемы для Проекта (Project)."""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from .user import User
from .service import Service
from .booking import Booking
from .subscriber import Subscriber


class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None


class Project(ProjectBase):
    id: int
    user_id: int
    api_key: str
    created_at: datetime
    updated_at: datetime
    user: User
    services: List[Service] = []
    bookings: List[Booking] = []
    subscribers: List[Subscriber] = []
    model_config = ConfigDict(from_attributes=True)


Project.model_rebuild()
