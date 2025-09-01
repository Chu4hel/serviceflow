"""
Management API: Эндпоинты для управления услугами.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.crud import crud_service, crud_project
from app.db.session import get_db
from app.models.serviceflow import User
from app.schemas import serviceflow as schemas

router = APIRouter()

@router.post("/projects/{project_id}/services", response_model=schemas.Service, status_code=201)
async def create_project_service(
    project_id: int,
    service: schemas.ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = await crud_project.get_project(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return await crud_service.create_service(db=db, project_id=project_id, service=service)


@router.get("/projects/{project_id}/services", response_model=List[schemas.Service])
async def read_project_services(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    project = await crud_project.get_project(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return await crud_service.get_services(db, project_id=project_id, skip=skip, limit=limit)
