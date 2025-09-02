"""
Модели базы данных SQLAlchemy для проекта ServiceFlow.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func, Numeric, UniqueConstraint, Boolean
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """Модель Пользователя."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Модель Проекта."""
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


class Service(Base):
    """Модель Услуги."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="services")
    bookings = relationship("Booking", back_populates="service")


class Booking(Base):
    """Модель Бронирования."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    booking_time = Column(DateTime, nullable=False)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(255), nullable=False)
    status = Column(String(50), default="new", nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")


class Subscriber(Base):
    """Модель Подписчика."""
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="subscribers")

    __table_args__ = (UniqueConstraint('project_id', 'email', name='_project_email_uc'),)
