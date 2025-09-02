"""
Public API: Эндпоинты для создания подписчика.
Требуют X-API-KEY.
"""
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_project_by_api_key
from app.crud import crud_subscriber
from app.db.session import get_db
from app.models.serviceflow import Project
from app.schemas import serviceflow as schemas

router = APIRouter()


@router.post(
    "/subscribers",
    response_model=schemas.Subscriber,
    status_code=status.HTTP_201_CREATED,
    summary="Создание или получение подписчика",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Subscriber,
            "description": "Подписчик с таким email уже существует. Возвращены данные существующего подписчика.",
        }
    },
)
async def create_public_subscriber(
        subscriber: schemas.SubscriberCreate,
        project: Project = Depends(get_project_by_api_key),
        db: AsyncSession = Depends(get_db),
        allow_duplicates: bool = False,
):
    """
    Создает нового подписчика или возвращает существующего.

    - По умолчанию (`allow_duplicates=False`), если подписчик с таким `email` уже существует в проекте, возвращаются его данные со статусом 200.
    - Если подписчик не найден, он создается и возвращается со статусом 201.
    - Если `allow_duplicates=True`, система всегда создает нового подписчика.
    """
    if not allow_duplicates:
        existing_subscriber = await crud_subscriber.get_subscriber_by_email_and_project(
            db, project_id=project.id, email=subscriber.email
        )
        if existing_subscriber:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=jsonable_encoder(existing_subscriber)
            )

    return await crud_subscriber.create_subscriber(db=db, project_id=project.id, subscriber=subscriber)
