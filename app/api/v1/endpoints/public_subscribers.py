"""
Public API: Эндпоинты для создания подписчика.
Требуют X-API-KEY.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_project_by_api_key
from app.crud import crud_subscriber
from app.db.session import get_db
from app.models.serviceflow import Project
from app.schemas import serviceflow as schemas

router = APIRouter()

@router.post("/subscribers", response_model=schemas.Subscriber, status_code=201)
async def create_public_subscriber(
    subscriber: schemas.SubscriberCreate,
    project: Project = Depends(get_project_by_api_key),
    db: AsyncSession = Depends(get_db),
):
    return await crud_subscriber.create_subscriber(db=db, project_id=project.id, subscriber=subscriber)
