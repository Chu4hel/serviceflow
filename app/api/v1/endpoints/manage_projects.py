"""
Management API: Эндпоинты для управления проектами.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.crud import crud_project
from app.db.session import get_db
from app.models.serviceflow import User
from app.schemas import serviceflow as schemas

router = APIRouter()

@router.post("/projects", response_model=schemas.Project, status_code=201)
async def create_user_project(
    project: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await crud_project.create_project(db=db, user_id=current_user.id, project=project)


@router.get("/projects", response_model=List[schemas.Project], summary="Получение списка проектов пользователя")
async def read_user_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    return await crud_project.get_projects_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
