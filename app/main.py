"""
Главный файл приложения FastAPI.
"""
from fastapi import FastAPI

# Импортируем роутеры
from app.api.v1.endpoints import (
    login,
    users,
    public_bookings,
    public_services,
    public_subscribers,
    manage_projects,
    manage_services,
    manage_bookings
)

app = FastAPI(
    title="ServiceFlow API",
    description="API для управления проектами, услугами и бронированиями.",
    version="1.0.0",
)

# Роутер для аутентификации
app.include_router(login.router, tags=["Auth"])

# Роутеры для Public API (требуют X-API-KEY)
app.include_router(public_services.router, prefix="/public/v1", tags=["Public API"])
app.include_router(public_bookings.router, prefix="/public/v1", tags=["Public API"])
app.include_router(public_subscribers.router, prefix="/public/v1", tags=["Public API"])

# Роутеры для Management API (требуют JWT)
app.include_router(users.router, prefix="/manage", tags=["Management API - Users"])
app.include_router(manage_projects.router, prefix="/manage", tags=["Management API - Projects"])
app.include_router(manage_services.router, prefix="/manage", tags=["Management API - Services"])
app.include_router(manage_bookings.router, prefix="/manage", tags=["Management API - Bookings"])


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to ServiceFlow API"}
