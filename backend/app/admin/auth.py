from __future__ import annotations

from starlette.requests import Request

from sqladmin.authentication import AuthenticationBackend

from app.admin.security import (
    SQLADMIN_SESSION_PERMISSIONS_KEY,
    SQLADMIN_SESSION_ROLES_KEY,
    SQLADMIN_SESSION_USER_ID_KEY,
    authenticate_sqladmin_login,
    can_access_sqladmin_roles,
    current_user_from_session,
)


class SQLAdminAuthBackend(AuthenticationBackend):
    """Session-based SQLAdmin auth for technical users only."""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username") or form.get("email") or "")
        password = str(form.get("password") or "")
        current_user = authenticate_sqladmin_login(email=email, password=password)
        if current_user is None:
            request.session.clear()
            return False

        request.session.update(
            {
                SQLADMIN_SESSION_USER_ID_KEY: str(current_user.id),
                SQLADMIN_SESSION_ROLES_KEY: sorted(current_user.roles),
                SQLADMIN_SESSION_PERMISSIONS_KEY: sorted(current_user.permissions),
            },
        )
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        session_user = current_user_from_session(request)
        if session_user is None:
            return False
        return can_access_sqladmin_roles(session_user["roles"])
