from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Request

from app.admin.masking import mask_json
from app.db.session import SessionLocal
from app.models.enums import ActorType
from app.services.audit_service import AuditService


def _actor_user_id_from_request(request: Request) -> UUID | None:
    try:
        value = request.session.get("sqladmin_user_id")
    except (AttributeError, AssertionError):
        return None
    try:
        return UUID(str(value)) if value else None
    except ValueError:
        return None


def _model_id(model: Any) -> UUID | None:
    value = getattr(model, "id", None)
    return value if isinstance(value, UUID) else None


def model_snapshot(model: Any) -> dict[str, Any]:
    table = getattr(model, "__table__", None)
    if table is None:
        return {}
    payload = {column.name: getattr(model, column.name, None) for column in table.columns}
    return mask_json(payload)


def record_admin_audit(
    request: Request,
    *,
    action: str,
    model: Any,
    before_json: dict[str, Any] | None = None,
    after_json: dict[str, Any] | None = None,
) -> None:
    with SessionLocal() as db:
        AuditService.record(
            db,
            actor_user_id=_actor_user_id_from_request(request),
            actor_type=ActorType.USER,
            action=action,
            entity_type=model.__class__.__name__,
            entity_id=_model_id(model),
            before_json=before_json or {},
            after_json=after_json or model_snapshot(model),
            context=AuditService.context_from_request(request),
        )
        db.commit()
