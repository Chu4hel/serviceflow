from pydantic import ConfigDict
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
    BACKEND_CORS_ORIGINS: list[str] = [
        "https://www.xn----dtbikdcfar9bfeeq.xn--p1ai",
        "https://xn----dtbikdcfar9bfeeq.xn--p1ai",
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
    ]

    # Добавляем переменную для тестовой БД
    TESTING: bool = False
    TEST_POSTGRES_DB: str = "test_db"


settings = Settings()
