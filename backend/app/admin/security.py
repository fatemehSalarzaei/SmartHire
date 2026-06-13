from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session

from app.core.auth import authenticate_user, build_current_user
from app.db.session import SessionLocal
from app.models.identity import User

SQLADMIN_WRITE_ROLES = frozenset({"SUPER_ADMIN", "SYSTEM_ADMIN"})
SQLADMIN_READ_ONLY_ROLES = frozenset({"TECH_SUPPORT", "READ_ONLY_AUDITOR"})
SQLADMIN_ALLOWED_ROLES = SQLADMIN_WRITE_ROLES | SQLADMIN_READ_ONLY_ROLES
HR_ROLE_CODES = frozenset({"HR_MANAGER", "RECRUITER", "REVIEWER"})


@dataclass(frozen=True)
class AdminAccess:
    allowed: bool
    read_only: bool
    roles: frozenset[str]


def _session_get(request: Request, key: str) -> Any:
    try:
        return request.session.get(key)
    except (AttributeError, AssertionError):
        return None


def _session_set(request: Request, key: str, value: Any) -> None:
    request.session[key] = value


def _session_clear(request: Request) -> None:
    try:
        request.session.clear()
    except (AttributeError, AssertionError):
        return


def evaluate_sqladmin_access(role_codes: set[str] | frozenset[str]) -> AdminAccess:
    roles = frozenset(role_codes)
    # HR-facing operational roles must never access /admin.
    if roles & HR_ROLE_CODES and not roles & SQLADMIN_WRITE_ROLES:
        return AdminAccess(allowed=False, read_only=True, roles=roles)
    if roles & SQLADMIN_WRITE_ROLES:
        return AdminAccess(allowed=True, read_only=False, roles=roles)
    if roles & SQLADMIN_READ_ONLY_ROLES:
        return AdminAccess(allowed=True, read_only=True, roles=roles)
    return AdminAccess(allowed=False, read_only=True, roles=roles)


def user_sqladmin_access(db: Session, user: User) -> AdminAccess:
    current_user = build_current_user(db, user)
    return evaluate_sqladmin_access(current_user.roles)


class SQLAdminAuthBackend(AuthenticationBackend):
    """SQLAdmin authentication for technical users only.

    This backend deliberately reuses SmartHire's internal email/password user store and role
    mappings. It does not trust frontend role hiding and it does not grant HR roles access to
    the technical `/admin` surface.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("email") or form.get("username") or "").strip()
        password = str(form.get("password") or "")
        if not email or not password:
            return False

        with SessionLocal() as db:
            user = authenticate_user(db, email=email, password=password)
            if user is None:
                return False
            access = user_sqladmin_access(db, user)
            if not access.allowed:
                return False
            _session_set(request, "sqladmin_user_id", str(user.id))
            _session_set(request, "sqladmin_roles", sorted(access.roles))
            _session_set(request, "sqladmin_read_only", access.read_only)
            db.commit()
            return True

    async def logout(self, request: Request) -> bool:
        _session_clear(request)
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = _session_get(request, "sqladmin_user_id")
        if not user_id:
            return False
        try:
            parsed_user_id = UUID(str(user_id))
        except (TypeError, ValueError):
            _session_clear(request)
            return False

        with SessionLocal() as db:
            user = db.get(User, parsed_user_id)
            if user is None or not user.is_active:
                _session_clear(request)
                return False
            access = user_sqladmin_access(db, user)
            if not access.allowed:
                _session_clear(request)
                return False
            _session_set(request, "sqladmin_roles", sorted(access.roles))
            _session_set(request, "sqladmin_read_only", access.read_only)
            return True


def request_sqladmin_roles(request: Request) -> frozenset[str]:
    roles = _session_get(request, "sqladmin_roles") or []
    return frozenset(str(role) for role in roles)


def request_has_write_access(request: Request) -> bool:
    return bool(request_sqladmin_roles(request) & SQLADMIN_WRITE_ROLES)


def request_has_read_only_access(request: Request) -> bool:
    access = evaluate_sqladmin_access(request_sqladmin_roles(request))
    return access.allowed and access.read_only
