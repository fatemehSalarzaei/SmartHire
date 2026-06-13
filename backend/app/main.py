from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(title=settings.app_name, version=settings.app_version)
    application.middleware("http")(request_id_middleware)
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(auth_router)
    return application


app = create_app()
