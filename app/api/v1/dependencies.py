"""
Зависимости для API, например, для получения текущего пользователя.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core import security
from app.crud import crud_user, crud_project
from app.db.session import get_db
from app.models import serviceflow as models
from app.schemas import serviceflow as schemas

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/login", auto_error=False
)


async def get_current_active_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(reusable_oauth2)
) -> Optional[models.User]:
    if not token:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
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


async def get_current_user(
        current_user: models.User = Depends(get_current_active_user)
) -> schemas.User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется аутентификация")
    return schemas.User.model_validate(current_user)


async def get_current_user_optional(
        current_user: Optional[models.User] = Depends(get_current_active_user)
) -> Optional[schemas.User]:
    if not current_user:
        return None
    return schemas.User.model_validate(current_user)


async def check_if_first_user_or_superuser(
        db: AsyncSession = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_active_user)
):
    result = await db.execute(select(func.count()).select_from(models.User))
    user_count = result.scalar_one()

    if user_count == 0:
        return  # Разрешаем, если это первый пользователь

    # Если пользователи уже есть, требуем аутентифицированного суперпользователя
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется аутентификация")
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения этого действия")


async def get_project_by_api_key(
        x_api_key: Optional[str] = Header(None, alias="X-API-KEY"),
        db: AsyncSession = Depends(get_db)
) -> models.Project:
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API ключ отсутствует"
        )

    project = await crud_project.get_project_by_apikey(db, api_key=x_api_key)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный API ключ"
        )
    return project


async def get_current_superuser(
        current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not current_user or not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для выполнения этого действия"
        )
    return current_user
