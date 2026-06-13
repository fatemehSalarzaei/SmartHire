from __future__ import annotations

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.security import SQLAdminAuthBackend
from app.admin.views import ADMIN_VIEWS
from app.core.config import settings
from app.db.session import engine


def mount_sqladmin(app: FastAPI) -> Admin | None:
    if not settings.enable_sqladmin:
        return None

    admin = Admin(
        app=app,
        engine=engine,
        base_url=settings.sqladmin_path,
        authentication_backend=SQLAdminAuthBackend(secret_key=settings.jwt_secret_key),
        title=f"{settings.app_name} Technical Admin",
    )
    for view in ADMIN_VIEWS:
        admin.add_view(view)
    return admin
