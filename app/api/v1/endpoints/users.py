"""
Management API: Эндпоинты для регистрации пользователей.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user
from app.db.session import get_db
from app.schemas import serviceflow as schemas

router = APIRouter()

@router.post("/users", response_model=schemas.User, status_code=201)
async def create_user_registration(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud_user.create_user(db=db, user=user)
