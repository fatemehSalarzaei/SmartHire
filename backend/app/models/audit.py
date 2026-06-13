from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SQLEnum

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import ActorType
from app.models.mixins import TimestampMixin


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_actor_created", "actor_user_id", "created_at"),)

    actor_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
    )
    actor_type: Mapped[ActorType] = mapped_column(SQLEnum(ActorType, name="actor_type"), nullable=False)
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    before_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    after_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(80))
    user_agent: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class IntegrationError(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "integration_errors"
    __table_args__ = (Index("ix_integration_errors_source_created", "source", "created_at"),)

    source: Mapped[str] = mapped_column(String(80), nullable=False)
    error_code: Mapped[str] = mapped_column(String(120), nullable=False)
    message_fa: Mapped[str] = mapped_column(Text, nullable=False)
    retryable: Mapped[bool] = mapped_column(nullable=False, default=False)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class WorkerTaskLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "worker_task_logs"

    task_name: Mapped[str] = mapped_column(String(160), nullable=False)
    task_id: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    queue_name: Mapped[str | None] = mapped_column(String(80))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(120))
    message_fa: Mapped[str | None] = mapped_column(Text)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
