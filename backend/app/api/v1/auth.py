from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser, authenticate_user, build_current_user, get_current_user
from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.core.responses import success_response
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.models.enums import ActorType
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1", tags=["auth"])


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    roles: list[str]
    permissions: list[str]


def _user_response(current_user: CurrentUser) -> dict[str, object]:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        roles=sorted(current_user.roles),
        permissions=sorted(current_user.permissions),
    ).model_dump()


@router.post("/auth/login", status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> dict[str, object]:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    audit_context = AuditService.context_from_request(request)

    if user is None:
        AuditService.record(
            db,
            action="LOGIN_FAILURE",
            entity_type="User",
            actor_user_id=None,
            actor_type=ActorType.USER,
            after_json={"email": _masked_email(payload.email)},
            context=audit_context,
        )
        db.commit()
        raise AppError(code=ErrorCode.INVALID_CREDENTIALS, status_code=401)

    current_user = build_current_user(db, user)
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        subject=str(user.id),
        email=user.email,
        expires_delta=expires_delta,
    )
    AuditService.record(
        db,
        action="LOGIN_SUCCESS",
        entity_type="User",
        actor_user_id=user.id,
        actor_type=ActorType.USER,
        entity_id=user.id,
        context=audit_context,
    )
    db.commit()

    return success_response(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": int(expires_delta.total_seconds()),
            "user": _user_response(current_user),
        },
    )


@router.get("/me", status_code=status.HTTP_200_OK)
def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> dict[str, object]:
    return success_response(_user_response(current_user))


def _masked_email(email: str) -> str:
    local, separator, domain = email.partition("@")
    if not separator:
        return "***"
    first = local[:1] or "*"
    return f"{first}***@{domain}"
