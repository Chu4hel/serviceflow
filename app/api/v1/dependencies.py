"""
Зависимости для API, например, для получения текущего пользователя.
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.core import security
from app.crud import crud_user, crud_project
from app.db.session import get_db
from app.models import serviceflow as models
from app.schemas import serviceflow as schemas

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/login"  # Указываем эндпоинт, который выдает токен
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud_user.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user
