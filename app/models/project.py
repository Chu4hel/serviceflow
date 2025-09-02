"""Модель Проекта (Project)."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    services = relationship("Service", back_populates="project", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="project", cascade="all, delete-orphan")
    subscribers = relationship("Subscriber", back_populates="project", cascade="all, delete-orphan")
