"""
Management API: Эндпоинты для управления проектами.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.services.project_service import ProjectService
from app.db.session import get_db
from app import models
from app import schemas

router = APIRouter()


@router.post(
    "/projects",
    response_model=schemas.Project,
    status_code=status.HTTP_201_CREATED,
    summary="Создание или получение проекта",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Project,
            "description": "Проект с таким именем уже существует. Возвращены данные существующего проекта.",
        }
    },
)
async def create_user_project(
        project_in: schemas.ProjectCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        allow_duplicates: bool = False
):
    """
    Создает новый проект или возвращает существующий, если имя совпадает.
    """
    project_service = ProjectService(db)
    # Проверяем, не был ли проект уже создан (для идемпотентности)
    original_name = project_in.name
    project = await project_service.create_project_for_user(
        project_in=project_in, current_user=current_user, allow_duplicates=allow_duplicates
    )

    # Если был возвращен существующий проект, меняем статус ответа на 200 OK
    if project.name == original_name and not allow_duplicates:
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(project))

    return project


@router.get("/projects", response_model=List[schemas.Project], summary="Получение списка проектов пользователя")
async def read_user_projects(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    project_service = ProjectService(db)
    projects = await project_service.get_projects_for_user(current_user=current_user, skip=skip, limit=limit)
    return projects


@router.get("/projects/{project_id}", response_model=schemas.Project, summary="Получение проекта по ID")
async def read_user_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    project_service = ProjectService(db)
    project = await project_service.get_project_for_user(project_id=project_id, current_user=current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден или у вас нет прав доступа")
    return project


@router.put("/projects/{project_id}", response_model=schemas.Project, summary="Обновление проекта")
async def update_user_project(
        project_id: int,
        project_in: schemas.ProjectUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    project_service = ProjectService(db)
    updated_project = await project_service.update_project_for_user(
        project_id=project_id, project_in=project_in, current_user=current_user
    )
    if not updated_project:
        raise HTTPException(status_code=404, detail="Проект не найден или у вас нет прав доступа")
    return updated_project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление проекта")
async def delete_user_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    project_service = ProjectService(db)
    success = await project_service.delete_project_for_user(project_id=project_id, current_user=current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Проект не найден или у вас нет прав доступа")
    return Response(status_code=status.HTTP_204_NO_CONTENT)