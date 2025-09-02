"""
Management API: Эндпоинты для управления подписчиками.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.crud import crud_subscriber, crud_project
from app.db.session import get_db
from app.models import serviceflow as models
from app.schemas import serviceflow as schemas

router = APIRouter()


@router.get("/projects/{project_id}/subscribers", response_model=List[schemas.Subscriber],
            summary="Получение списка подписчиков проекта")
async def read_project_subscribers(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    subscribers = await crud_subscriber.get_subscribers(
        db, project_id=project_id, current_user=current_user, skip=skip, limit=limit
    )
    if not subscribers:
        project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")
    return subscribers


@router.get("/projects/{project_id}/subscribers/{subscriber_id}", response_model=schemas.Subscriber,
            summary="Получение подписчика по ID")
async def read_project_subscriber(
        project_id: int,
        subscriber_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    subscriber = await crud_subscriber.get_subscriber(db, subscriber_id=subscriber_id, current_user=current_user)
    if not subscriber or subscriber.project_id != project_id:
        raise HTTPException(status_code=404, detail="Подписчик не найден или не принадлежит указанному проекту")
    return subscriber


@router.delete("/projects/{project_id}/subscribers/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удаление подписчика")
async def delete_project_subscriber(
        project_id: int,
        subscriber_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    subscriber = await crud_subscriber.get_subscriber(db, subscriber_id=subscriber_id, current_user=current_user)
    if not subscriber or subscriber.project_id != project_id:
        raise HTTPException(status_code=404, detail="Подписчик не найден или не принадлежит указанному проекту")

    await crud_subscriber.delete_subscriber(db=db, db_obj=subscriber)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
