"""
Сервисный слой для управления услугами.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_service
from app.services.project_service import ProjectService
from app import models
from app import schemas


class ServiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)

    async def get_service_for_user(
            self, service_id: int, current_user: models.User
    ) -> Optional[models.Service]:
        """Получает услугу по ID, проверяя права доступа через проект."""
        service = await crud_service.get_service(self.db, service_id=service_id)
        if not service:
            return None
        # Проверяем, имеет ли пользователь доступ к проекту, которому принадлежит услуга
        project = await self.project_service.get_project_for_user(project_id=service.project_id,
                                                                  current_user=current_user)
        if not project:
            return None
        return service

    async def get_services_for_user(
            self, project_id: int, current_user: models.User, skip: int, limit: int
    ) -> Optional[List[models.Service]]:
        """Получает список услуг для проекта, проверяя права доступа."""
        project = await self.project_service.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return None  # Возвращаем None, если проекта нет или нет доступа
        return await crud_service.get_services(self.db, project_id=project_id, skip=skip, limit=limit)

    async def create_service_for_user(
            self, project_id: int, service_in: schemas.ServiceCreate, current_user: models.User,
            allow_duplicates: bool = False
    ) -> Optional[models.Service]:
        """Создает услугу в проекте, проверяя права доступа."""
        project = await self.project_service.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return None

        if not allow_duplicates:
            existing_service = await crud_service.get_service_by_name_and_project(
                self.db, project_id=project_id, name=service_in.name
            )
            if existing_service:
                return existing_service

        return await crud_service.create_service(self.db, project_id=project_id, service=service_in)

    async def update_service_for_user(
            self, service_id: int, service_in: schemas.ServiceUpdate, current_user: models.User
    ) -> Optional[models.Service]:
        """Обновляет услугу, проверяя права доступа."""
        service = await self.get_service_for_user(service_id=service_id, current_user=current_user)
        if not service:
            return None
        return await crud_service.update_service(self.db, db_obj=service, obj_in=service_in)

    async def delete_service_for_user(self, service_id: int, current_user: models.User) -> bool:
        """Удаляет услугу, проверяя права доступа."""
        service = await self.get_service_for_user(service_id=service_id, current_user=current_user)
        if not service:
            return False
        await crud_service.delete_service(self.db, db_obj=service)
        return True
