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
from app.crud import crud_project
from app.db.session import get_db
from app.models import serviceflow as models
from app.schemas import serviceflow as schemas

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
        project: schemas.ProjectCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        allow_duplicates: bool = False
):
    """
    Создает новый проект или возвращает существующий, если имя совпадает.

    - По умолчанию (`allow_duplicates=False`), если проект с таким `name` уже существует у пользователя, возвращаются его данные со статусом 200.
    - Если проект не найден, он создается и возвращается со статусом 201.
    - Если `allow_duplicates=True`, система всегда создает новый проект.
    """
    if not allow_duplicates:
        existing_project = await crud_project.get_project_by_name(db, name=project.name, current_user=current_user)
        if existing_project:
            # Возвращаем существующий проект, он уже содержит все связи
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(existing_project))

    # Создаем новый проект, если дубликаты разрешены или существующий не найден
    new_project = await crud_project.create_project(db=db, user_id=current_user.id, project_in=project)
    return new_project


@router.get("/projects", response_model=List[schemas.Project], summary="Получение списка проектов пользователя")
async def read_user_projects(
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100,
):
    return await crud_project.get_projects(db, current_user=current_user, skip=skip, limit=limit)


@router.get("/projects/{project_id}", response_model=schemas.Project, summary="Получение проекта по ID")
async def read_user_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
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
    project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден или у вас нет прав доступа")
    updated_project = await crud_project.update_project(db=db, db_obj=project, obj_in=project_in)
    return updated_project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление проекта")
async def delete_user_project(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден или у вас нет прав доступа")
    await crud_project.delete_project(db=db, db_obj=project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
