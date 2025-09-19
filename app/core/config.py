from typing import Union, List

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(frozen=False, env_file=".env", extra="ignore")

    # Переменные для контейнера БД
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432

    # Переменные для приложения
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Переменная для CORS
    BACKEND_CORS_ORIGINS: Union[str, list[str]] = [
        "https://www.xn----dtbikdcfar9bfeeq.xn--p1ai",
        "https://xn----dtbikdcfar9bfeeq.xn--p1ai",
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
    ]

    # Этот валидатор сработает ДО того, как Pydantic проверит тип.
    # Он возьмет строку из .env или переменных Render и превратит ее в список.
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            # Если это простая строка с запятыми, делим ее
            return [i.strip() for i in v.split(",")]
        # Если это уже список или JSON-строка, Pydantic сам справится
        return v

    # Добавляем переменную для тестовой БД
    TESTING: bool = False
    TEST_POSTGRES_DB: str = "test_db"


settings = Settings()
