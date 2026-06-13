from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SQLEnum

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import PriorityBucket
from app.models.mixins import TimestampMixin


class ScreeningScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_scores"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="screening_score_range"),
        Index("ix_screening_scores_application_created", "screening_application_id", "created_at"),
    )

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    score_breakdown_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ruleset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    ruleset_version: Mapped[int | None] = mapped_column(Integer)


class RankingResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ranking_results"

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    kando_job_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_in_job: Mapped[int | None] = mapped_column(Integer)
    priority_bucket: Mapped[PriorityBucket | None] = mapped_column(
        SQLEnum(PriorityBucket, name="priority_bucket"),
    )
    score: Mapped[int | None] = mapped_column(Integer)
    ranking_scope: Mapped[str | None] = mapped_column(String(80))
    score_breakdown_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

