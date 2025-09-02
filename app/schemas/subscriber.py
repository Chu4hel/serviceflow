"""Pydantic схемы для Подписчика (Subscriber)."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime


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
