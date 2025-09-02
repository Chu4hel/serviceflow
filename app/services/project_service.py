"""
Сервисный слой для управления проектами.

Этот слой содержит бизнес-логику, связанную с проектами, и выступает
посредником между API-эндпоинтами и CRUD-операциями.
"""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_project
from app import models
from app import schemas


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_for_user(
            self, project_id: int, current_user: models.User
    ) -> Optional[models.Project]:
        """Получает проект по ID, проверяя права доступа пользователя."""
        project = await crud_project.get_project(self.db, project_id=project_id)
        if not project:
            return None
        if not current_user.is_superuser and (project.user_id != current_user.id):
            return None
        return project

    async def get_projects_for_user(
            self, current_user: models.User, skip: int, limit: int
    ) -> List[models.Project]:
        """Получает список проектов для пользователя с учетом его прав."""
        if current_user.is_superuser:
            # Суперпользователь получает все проекты
            return await crud_project.get_projects(self.db, skip=skip, limit=limit)
        else:
            # Обычный пользователь получает только свои проекты
            return await crud_project.get_projects(self.db, user_id=current_user.id, skip=skip, limit=limit)

    async def create_project_for_user(
            self, project_in: schemas.ProjectCreate, current_user: models.User, allow_duplicates: bool = False
    ) -> models.Project:
        """Создает проект для пользователя, с проверкой на дубликаты."""
        if not allow_duplicates:
            existing_project = await crud_project.get_project_by_name(
                self.db, name=project_in.name, user_id=current_user.id
            )
            if existing_project:
                return existing_project

        return await crud_project.create_project(self.db, user_id=current_user.id, project_in=project_in)

    async def update_project_for_user(
            self, project_id: int, project_in: schemas.ProjectUpdate, current_user: models.User
    ) -> Optional[models.Project]:
        """Обновляет проект, предварительно проверив права доступа."""
        project = await self.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return None
        return await crud_project.update_project(self.db, db_obj=project, obj_in=project_in)

    async def delete_project_for_user(self, project_id: int, current_user: models.User) -> bool:
        """Удаляет проект, предварительно проверив права доступа."""
        project = await self.get_project_for_user(project_id=project_id, current_user=current_user)
        if not project:
            return False
        await crud_project.delete_project(self.db, db_obj=project)
        return True
