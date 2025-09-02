"""
Management API: Эндпоинты для управления услугами.
Требуют JWT аутентификации.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.crud import crud_service, crud_project
from app.db.session import get_db
from app.models import serviceflow as models
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
        current_user: models.User = Depends(get_current_active_user),
        allow_duplicates: bool = False
):
    """
    Создает новую услугу или возвращает существующую, если имя совпадает.
    Доступно только владельцу проекта.
    """
    # Проверяем, что у пользователя есть доступ к проекту
    project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")

    if not allow_duplicates:
        existing_service = await crud_service.get_service_by_name_and_project(
            db, project_id=project_id, name=service.name, current_user=current_user
        )
        if existing_service:
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(existing_service))

    return await crud_service.create_service(db=db, project_id=project_id, service=service)


@router.get("/projects/{project_id}/services", response_model=List[schemas.Service],
            summary="Получение списка услуг проекта")
async def read_project_services(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100
):
    # crud_service.get_services теперь сам проверяет права доступа
    services = await crud_service.get_services(db, project_id=project_id, current_user=current_user, skip=skip, limit=limit)
    # Дополнительная проверка, если get_services вернет пустой список, потому что проекта нет
    if not services:
        project = await crud_project.get_project(db, project_id=project_id, current_user=current_user)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")
    return services


@router.get("/projects/{project_id}/services/{service_id}", response_model=schemas.Service, summary="Получение услуги по ID")
async def read_project_service(
    project_id: int,
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    service = await crud_service.get_service(db, service_id=service_id, current_user=current_user)
    if not service or service.project_id != project_id:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")
        
    return service


@router.put("/projects/{project_id}/services/{service_id}", response_model=schemas.Service, summary="Обновление услуги")
async def update_project_service(
    project_id: int,
    service_id: int,
    service_in: schemas.ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    service = await crud_service.get_service(db, service_id=service_id, current_user=current_user)
    if not service or service.project_id != project_id:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")

    updated_service = await crud_service.update_service(db=db, db_obj=service, obj_in=service_in)
    return updated_service


@router.delete("/projects/{project_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление услуги")
async def delete_project_service(
    project_id: int,
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    service = await crud_service.get_service(db, service_id=service_id, current_user=current_user)
    if not service or service.project_id != project_id:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")

    await crud_service.delete_service(db=db, db_obj=service)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
