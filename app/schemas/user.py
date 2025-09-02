"""Pydantic схемы для Пользователя (User)."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
