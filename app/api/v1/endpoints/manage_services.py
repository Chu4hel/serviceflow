"""
Management API: Эндпоинты для управления услугами.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user
from app.services.service_service import ServiceService
from app.db.session import get_db
from app import models
from app import schemas

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
        service_in: schemas.ServiceCreate,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        allow_duplicates: bool = False
):
    service_service = ServiceService(db)
    original_name = service_in.name
    service = await service_service.create_service_for_user(
        project_id=project_id, service_in=service_in, current_user=current_user, allow_duplicates=allow_duplicates
    )
    if not service:
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")

    if service.name == original_name and not allow_duplicates:
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(service))

    return service


@router.get("/projects/{project_id}/services", response_model=List[schemas.Service],
            summary="Получение списка услуг проекта")
async def read_project_services(
        project_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
        skip: int = 0,
        limit: int = 100
):
    service_service = ServiceService(db)
    services = await service_service.get_services_for_user(
        project_id=project_id, current_user=current_user, skip=skip, limit=limit
    )
    if services is None:  # Сервис возвращает None если проекта нет или нет доступа
        raise HTTPException(status_code=404, detail="Проект не найден или доступ запрещен")
    return services


@router.get("/projects/{project_id}/services/{service_id}", response_model=schemas.Service,
            summary="Получение услуги по ID")
async def read_project_service(
        project_id: int,
        service_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    service_service = ServiceService(db)
    service = await service_service.get_service_for_user(service_id=service_id, current_user=current_user)
    if not service or service.project_id != project_id:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")

    return service
    service_service = ServiceService(db)
    service = await service_service.get_service_for_user(service_id=service_id, current_user=current_user)
    if not service:
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
    service_service = ServiceService(db)
    service = await service_service.update_service_for_user(
        service_id=service_id, service_in=service_in, current_user=current_user
    )
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")
    return service


@router.delete("/projects/{project_id}/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Удаление услуги")
async def delete_project_service(
        service_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user),
):
    service_service = ServiceService(db)
    success = await service_service.delete_service_for_user(service_id=service_id, current_user=current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Услуга не найдена или не принадлежит указанному проекту")
    return Response(status_code=status.HTTP_204_NO_CONTENT)