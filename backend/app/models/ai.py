from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SQLEnum

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import AIAnalysisStatus
from app.models.mixins import TimestampMixin


class AIAnalysisRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_analysis_runs"
    __table_args__ = (
        CheckConstraint(
            "error_code IS NULL OR error_message_fa IS NOT NULL",
            name="ai_error_message_fa_required",
        ),
        Index("ix_ai_analysis_runs_application_status", "screening_application_id", "status"),
    )

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    ruleset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    ruleset_version: Mapped[int | None] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(120), nullable=False)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(80), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[AIAnalysisStatus] = mapped_column(
        SQLEnum(AIAnalysisStatus, name="ai_analysis_status"),
        nullable=False,
        default=AIAnalysisStatus.PENDING,
    )
    error_code: Mapped[str | None] = mapped_column(String(120))
    error_message_fa: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AIAnalysisResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_analysis_results"
    __table_args__ = (
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="confidence_range"),
    )

    ai_analysis_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("ai_analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    output_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_signals_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence: Mapped[float | None] = mapped_column()

