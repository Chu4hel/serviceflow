"""
Главный файл приложения FastAPI.
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, HTMLResponse

# Импортируем роутеры
from app.api.v1.endpoints import (
    login,
    users,
    public_bookings,
    public_services,
    public_subscribers,
    manage_projects,
    manage_services,
    manage_bookings,
    manage_subscribers
)
from app.core.config import settings

# Метаданные для тегов Swagger
tags_metadata = [
    {"name": "Auth", "description": "Аутентификация и получение токена"},
    {"name": "Public API", "description": "Публичные эндпоинты, требующие X-API-KEY"},
    {"name": "Management API - Users", "description": "Управление пользователями (требует JWT)"},
    {"name": "Management API - Projects", "description": "Управление проектами (требует JWT)"},
    {"name": "Management API - Services", "description": "Управление услугами (требует JWT)"},
    {"name": "Management API - Bookings", "description": "Управление бронированиями (требует JWT)"},
    {"name": "Management API - Subscribers", "description": "Управление подписчиками (требует JWT)"},
]

app = FastAPI(
    title="ServiceFlow API",
    description="API для управления проектами, услугами и бронированиями.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=None,  # Отключаем стандартный docs
    redoc_url=None,  # Отключаем redoc
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования HTTP-запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Запрос: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Ответ: {response.status_code} (обработано за {process_time:.2f}с)")
    return response


# Словарь для перевода стандартных ошибок Pydantic
TRANSLATION_MAP = {
    "Field required": "Это поле обязательно",
    "Input should be a valid integer": "Значение должно быть целым числом",
    "Input should be a valid string": "Значение должно быть строкой",
    "Input should be a valid email address": "Введите корректный email адрес",
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    new_errors = []
    for error in exc.errors():
        new_msg = TRANSLATION_MAP.get(error["msg"], error["msg"])  # Переводим, если есть в словаре
        new_errors.append({
            "loc": error["loc"],
            "msg": new_msg,
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={"detail": new_errors},
    )


# Роутер для аутентификации
app.include_router(login.router, tags=["Auth"])

# Роутеры для Public API (требуют X-API-KEY)
app.include_router(public_services.router, prefix="/public/v1", tags=["Public API"])
app.include_router(public_bookings.router, prefix="/public/v1", tags=["Public API"])
app.include_router(public_subscribers.router, prefix="/public/v1", tags=["Public API"])

# Роутеры для Management API (требуют JWT)
app.include_router(users.router, prefix="/manage", tags=["Management API - Users"])
app.include_router(manage_projects.router, prefix="/manage", tags=["Management API - Projects"])
app.include_router(manage_services.router, prefix="/manage", tags=["Management API - Services"])
app.include_router(manage_bookings.router, prefix="/manage", tags=["Management API - Bookings"])
app.include_router(manage_subscribers.router, prefix="/manage", tags=["Management API - Subscribers"])


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to ServiceFlow API"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html_with_translation():
    # Получаем стандартный HTML от FastAPI
    default_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_ui_parameters={"lang": "ru"}  # Передаем параметр для базовой русификации
    ).body.decode()

    # Наш JavaScript для перевода оставшихся частей
    custom_script = '''
        <script>
            window.addEventListener("load", () => {
                const translations = {
                    'Parameters': 'Параметры',
                    'Request body': 'Тело запроса',
                    'Server response': 'Ответ сервера',
                    'Servers': 'Серверы',
                    'Schemas': 'Схемы',
                    'Code': 'Код',
                    'Description': 'Описание',
                    'Media type': 'Тип данных',
                    'Links': 'Ссылки',
                    'Authorize': 'Авторизация',
                    'No parameters': 'Нет параметров',
                    'Download': 'Скачать',
                    'Example': 'Пример',
                    'Example value': 'Пример значения'
                    // Добавьте другие переводы по необходимости
                };

                const translateNode = (node) => {
                    // Мы работаем только с текстовыми узлами
                    if (node.nodeType === Node.TEXT_NODE) {
                        const originalText = node.nodeValue.trim();
                        if (translations[originalText]) {
                            node.nodeValue = translations[originalText];
                        }
                    } 
                    // Рекурсивно обходим все дочерние узлы
                    else if (node.childNodes && node.childNodes.length > 0) {
                        node.childNodes.forEach(child => translateNode(child));
                    }
                };

                const observer = new MutationObserver((mutations, obs) => {
                    // Для каждой мутации мы запускаем перевод всего документа
                    translateNode(document.body);
                });

                // Начинаем наблюдение
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });

                // Первичный перевод на случай, если что-то уже отрендерилось
                translateNode(document.body);
            });
        </script>
    '''

    # Вставляем наш скрипт перед закрывающим тегом </body>
    custom_html = default_html.replace("</body>", custom_script + "</body>")

    return HTMLResponse(content=custom_html)
