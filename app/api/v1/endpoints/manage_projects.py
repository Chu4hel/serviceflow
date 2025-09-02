"""
Management API: Эндпоинты для управления проектами.
Требуют JWT аутентификации.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.crud import crud_project
from app.db.session import get_db
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
    current_user: schemas.User = Depends(get_current_user),
    allow_duplicates: bool = False
):
    """
    Создает новый проект или возвращает существующий, если имя совпадает.

    - По умолчанию (`allow_duplicates=False`), если проект с таким `name` уже существует у пользователя, возвращаются его данные со статусом 200.
    - Если проект не найден, он создается и возвращается со статусом 201.
    - Если `allow_duplicates=True`, система всегда создает новый проект.
    """
    if not allow_duplicates:
        existing_project = await crud_project.get_project_by_name_and_user(db, user_id=current_user.id, name=project.name)
        if existing_project:
            # Возвращаем существующий проект, предварительно загрузив все связи через get_project
            project_with_relations = await crud_project.get_project(db, project_id=existing_project.id)
            # Преобразуем в схему Pydantic для корректной сериализации
            project_schema = schemas.Project.model_validate(project_with_relations)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(project_schema))

    # Создаем новый проект, если дубликаты разрешены или существующий не найден
    new_project = await crud_project.create_project(db=db, user_id=current_user.id, project_in=project)
    return new_project


@router.get("/projects", response_model=List[schemas.Project], summary="Получение списка проектов пользователя")
async def read_user_projects(
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
):
    return await crud_project.get_projects_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
