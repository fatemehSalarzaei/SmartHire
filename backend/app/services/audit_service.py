from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.middleware import get_request_id
from app.models.audit import AuditLog
from app.models.enums import ActorType


@dataclass(frozen=True)
class AuditContext:
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


class AuditService:
    @staticmethod
    def context_from_request(request: Request) -> AuditContext:
        return AuditContext(
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=get_request_id(request),
        )

    @staticmethod
    def record(
        db: Session,
        *,
        action: str,
        entity_type: str,
        actor_user_id: UUID | None = None,
        actor_type: ActorType = ActorType.USER,
        entity_id: UUID | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
        context: AuditContext | None = None,
    ) -> AuditLog:
        context = context or AuditContext()
        audit_log = AuditLog(
            actor_user_id=actor_user_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_json=before_json or {},
            after_json=after_json or {},
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            request_id=context.request_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(audit_log)
        db.flush()
        return audit_log
