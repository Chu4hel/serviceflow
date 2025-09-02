"""
Management API: Эндпоинты для управления услугами.
Требуют JWT аутентификации.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.crud import crud_service, crud_project
from app.db.session import get_db
from app.schemas import serviceflow as schemas

router = APIRouter()


@router.post(
    "/projects/{project_id}/services",
    response_model=schemas.Service,
    status_code=status.HTTP_201_CREATED,
    summary="Создание или получение услуги",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Service,
            "description": "Услуга с таким именем уже существует. Возвращены данные существующей услуги.",
        }
    },
)
async def create_project_service(
        project_id: int,
        service: schemas.ServiceCreate,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user),
        allow_duplicates: bool = False
):
    """
    Создает новую услугу или возвращает существующую, если имя совпадает.

    - По умолчанию (`allow_duplicates=False`), если услуга с таким `name` уже существует в проекте, возвращаются ее данные со статусом 200.
    - Если услуга не найдена, она создается и возвращается со статусом 201.
    - Если `allow_duplicates=True`, система всегда создает новую услугу.
    """
    project = await crud_project.get_project(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")

    if not allow_duplicates:
        existing_service = await crud_service.get_service_by_name_and_project(db, project_id=project_id,
                                                                              name=service.name)
        if existing_service:
            service_with_relations = await crud_service.get_service(db, service_id=existing_service.id)
            service_schema = schemas.Service.model_validate(service_with_relations)
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(service_schema))

    return await crud_service.create_service(db=db, project_id=project_id, service=service)


@router.get("/projects/{project_id}/services", response_model=List[schemas.Service],
            summary="Получение списка услуг проекта")
async def read_project_services(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100
):
    project = await crud_project.get_project(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")
    return await crud_service.get_services(db, project_id=project_id, skip=skip, limit=limit)
