from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLEnum

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import (
    InternalStatus,
    MissingDataPolicy,
    PriorityBucket,
    RankingScope,
    RuleGroupType,
    RuleOperator,
    RuleSetStatus,
    RuleType,
)
from app.models.mixins import TimestampMixin


class ScreeningApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_applications"
    __table_args__ = (
        CheckConstraint(
            "priority_score IS NULL OR (priority_score >= 0 AND priority_score <= 100)",
            name="priority_score_range",
        ),
        Index("ix_screening_applications_job_status", "kando_job_id", "internal_status"),
        Index("ix_screening_applications_bucket_score", "priority_bucket", "priority_score"),
        Index("ix_screening_applications_snapshot_hash", "snapshot_hash"),
        Index(
            "uq_screening_applications_latest_kando_application",
            "kando_application_id",
            unique=True,
        ),
    )

    kando_application_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kando_candidate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kando_cv_id: Mapped[int | None] = mapped_column(Integer)
    kando_job_id: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_full_name: Mapped[str | None] = mapped_column(String(255))
    source_name: Mapped[str | None] = mapped_column(String(255))
    kando_hire_step_id: Mapped[int | None] = mapped_column(Integer)
    kando_status_id: Mapped[int | None] = mapped_column(Integer)
    internal_status: Mapped[InternalStatus] = mapped_column(
        SQLEnum(InternalStatus, name="internal_status"),
        nullable=False,
        default=InternalStatus.NOT_REVIEWED,
    )
    priority_score: Mapped[int | None] = mapped_column(Integer)
    priority_bucket: Mapped[PriorityBucket | None] = mapped_column(
        SQLEnum(PriorityBucket, name="priority_bucket"),
    )
    rank_in_job: Mapped[int | None] = mapped_column(Integer)
    snapshot_hash: Mapped[str | None] = mapped_column(String(128))
    raw_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_screened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_ranked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    screening_runs: Mapped[list["ScreeningRunItem"]] = relationship(
        back_populates="screening_application",
    )


class ScreeningRuleSet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_rulesets"
    __table_args__ = (
        CheckConstraint("version > 0", name="ruleset_version_positive"),
        CheckConstraint("max_score > 0", name="ruleset_max_score_positive"),
        Index(
            "uq_screening_rulesets_active_per_job",
            "kando_job_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    kando_job_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RuleSetStatus] = mapped_column(
        SQLEnum(RuleSetStatus, name="ruleset_status"),
        nullable=False,
        default=RuleSetStatus.DRAFT,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_missing_data_policy: Mapped[MissingDataPolicy] = mapped_column(
        SQLEnum(MissingDataPolicy, name="missing_data_policy"),
        nullable=False,
        default=MissingDataPolicy.NEEDS_REVIEW,
    )
    scoring_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    ranking_scope: Mapped[RankingScope] = mapped_column(
        SQLEnum(RankingScope, name="ranking_scope"),
        nullable=False,
        default=RankingScope.JOB,
    )
    config_hash: Mapped[str | None] = mapped_column(String(128))

    groups: Mapped[list["ScreeningRuleGroup"]] = relationship(back_populates="ruleset")


class ScreeningRuleGroup(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_rule_groups"

    ruleset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_rulesets.id", ondelete="CASCADE"),
        nullable=False,
    )
    group_type: Mapped[RuleGroupType] = mapped_column(
        SQLEnum(RuleGroupType, name="rule_group_type"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    ruleset: Mapped[ScreeningRuleSet] = relationship(back_populates="groups")
    rules: Mapped[list["ScreeningRule"]] = relationship(back_populates="group")


class ScreeningRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_rules"

    group_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_rule_groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_type: Mapped[RuleType] = mapped_column(SQLEnum(RuleType, name="rule_type"), nullable=False)
    field_path: Mapped[str] = mapped_column(String(255), nullable=False)
    operator: Mapped[RuleOperator] = mapped_column(
        SQLEnum(RuleOperator, name="rule_operator"),
        nullable=False,
    )
    value_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    score_delta: Mapped[int | None] = mapped_column(Integer)
    reason_code: Mapped[str | None] = mapped_column(String(120))
    message_fa: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    group: Mapped[ScreeningRuleGroup] = relationship(back_populates="rules")
    terms: Mapped[list["ScreeningRuleTerm"]] = relationship(back_populates="rule")


class ScreeningRuleTerm(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_rule_terms"

    rule_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_path: Mapped[str] = mapped_column(String(255), nullable=False)
    operator: Mapped[RuleOperator] = mapped_column(
        SQLEnum(RuleOperator, name="rule_operator"),
        nullable=False,
    )
    value_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    rule: Mapped[ScreeningRule] = relationship(back_populates="terms")


class ScreeningRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_runs"

    ruleset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_rulesets.id"),
    )
    ruleset_version: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    run_context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    items: Mapped[list["ScreeningRunItem"]] = relationship(back_populates="run")


class ScreeningRunItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_run_items"

    screening_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    run: Mapped[ScreeningRun] = relationship(back_populates="items")
    screening_application: Mapped[ScreeningApplication] = relationship(
        back_populates="screening_runs",
    )


class ScreeningDecision(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_decisions"
    __table_args__ = (
        Index("ix_screening_decisions_application_created", "screening_application_id", "created_at"),
    )

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    internal_status: Mapped[InternalStatus] = mapped_column(
        SQLEnum(InternalStatus, name="internal_status"),
        nullable=False,
    )
    ruleset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    ruleset_version: Mapped[int | None] = mapped_column(Integer)
    reasons_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    message_fa: Mapped[str | None] = mapped_column(Text)
