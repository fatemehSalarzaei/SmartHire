from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.core.security import decode_access_token, verify_password
from app.db.session import get_db_session
from app.models.enums import ActorType
from app.models.identity import Permission, Role, RolePermission, User, UserRole
from app.services.audit_service import AuditService

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    email: str
    full_name: str | None
    roles: frozenset[str]
    permissions: frozenset[str]


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    user = db.execute(
        select(User).where(func.lower(User.email) == email.strip().lower()),
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    return user


def build_current_user(db: Session, user: User) -> CurrentUser:
    role_codes = frozenset(
        db.execute(
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id),
        )
        .scalars()
        .all(),
    )
    permission_codes = frozenset(
        db.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user.id),
        )
        .scalars()
        .all(),
    )
    return CurrentUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=role_codes,
        permissions=permission_codes,
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db_session)],
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)

    payload = decode_access_token(credentials.credentials)
    try:
        user_id = UUID(str(payload["sub"]))
    except (KeyError, ValueError):
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401) from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)

    return build_current_user(db, user)


def require_permission(permission_code: str):
    def dependency(
        request: Request,
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if permission_code in current_user.permissions:
            return current_user

        try:
            AuditService.record(
                db,
                actor_user_id=current_user.id,
                actor_type=ActorType.USER,
                action="PERMISSION_DENIED",
                entity_type="Permission",
                after_json={"permission": permission_code},
                context=AuditService.context_from_request(request),
            )
            db.commit()
        except Exception:
            db.rollback()

        raise AppError(code=ErrorCode.PERMISSION_DENIED, status_code=403)

    return dependency
