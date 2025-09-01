"""
Эндпоинт для аутентификации и получения JWT-токена.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.crud import crud_user
from app.db.session import get_db

router = APIRouter()

@router.post("/auth/login")
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Аутентифицирует пользователя и возвращает JWT-токен.
    Использует OAuth2PasswordRequestForm, который ожидает form-data с полями
    `username` (здесь это email) и `password`.
    """
    user = await crud_user.get_user_by_email(db, email=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
