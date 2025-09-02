"""
Management API: Эндпоинты для регистрации пользователей.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import check_if_first_user_or_superuser
from app.crud import crud_user
from app.db.session import get_db
from app.schemas import serviceflow as schemas

router = APIRouter()


@router.post("/users", response_model=schemas.User, status_code=201,
             summary="Создание нового пользователя (только для суперпользователей)")
async def create_user_registration(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db),
        _: None = Depends(check_if_first_user_or_superuser)  # Защищаем эндпоинт
):
    """
    Создает нового пользователя. Доступно только для суперпользователей.
    Первый созданный пользователь в системе автоматически становится суперпользователем.
    """
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован")
    return await crud_user.create_user(db=db, user=user)
