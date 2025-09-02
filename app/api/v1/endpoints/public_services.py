"""
Public API: Эндпоинты для получения списка услуг.
Требуют X-API-KEY.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_project_by_api_key
from app.crud import crud_service
from app.db.session import get_db
from app import models
from app import schemas

router = APIRouter()

@router.get("/services", response_model=List[schemas.Service], summary="Получение списка публичных услуг")
async def read_public_services(
        project: models.Project = Depends(get_project_by_api_key),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    return await crud_service.get_services(db, project_id=project.id, skip=skip, limit=limit)
