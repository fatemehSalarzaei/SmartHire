from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.mixins import TimestampMixin


class KandoConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_connections"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    ats_base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    basedata_base_url: Mapped[str | None] = mapped_column(String(500))
    api_header_key: Mapped[str | None] = mapped_column(String(120))
    encrypted_api_key: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)


class KandoSyncState(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_sync_states"
    __table_args__ = (UniqueConstraint("sync_name", name="uq_kando_sync_states_sync_name"),)

    sync_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cursor_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class KandoRawPayload(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_raw_payloads"

    source: Mapped[str] = mapped_column(String(80), nullable=False)
    external_id: Mapped[int | None] = mapped_column(Integer)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    payload_hash: Mapped[str | None] = mapped_column(String(128))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class KandoApiCallLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_api_call_logs"

    method: Mapped[str] = mapped_column(String(12), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_code: Mapped[str | None] = mapped_column(String(120))
    message_fa: Mapped[str | None] = mapped_column(Text)


class KandoJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_jobs"

    kando_job_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(String(255))
    raw_payload_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_raw_payloads.id"),
    )


class KandoHireStep(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_hire_steps"
    __table_args__ = (
        UniqueConstraint("kando_hire_step_id", name="uq_kando_hire_steps_kando_hire_step_id"),
    )

    kando_hire_step_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kando_job_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(255))


class KandoApplicationSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_application_sources"
    __table_args__ = (
        UniqueConstraint(
            "kando_application_source_id",
            name="uq_kando_application_sources_kando_application_source_id",
        ),
    )

    kando_application_source_id: Mapped[int | None] = mapped_column(Integer)
    kando_cv_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_letter: Mapped[str | None] = mapped_column(Text)
    total_work_experience_months: Mapped[int | None] = mapped_column(Integer)


class KandoCandidate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_candidates"

    kando_candidate_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    raw_payload_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_raw_payloads.id"),
    )


class KandoCv(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_cvs"

    kando_cv_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    kando_candidate_id: Mapped[int | None] = mapped_column(Integer)
    raw_payload_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_raw_payloads.id"),
    )

    work_experiences: Mapped[list["KandoCvWorkExperience"]] = relationship(back_populates="cv")
    university_degrees: Mapped[list["KandoCvUniversityDegree"]] = relationship(back_populates="cv")
    language_skills: Mapped[list["KandoCvLanguageSkill"]] = relationship(back_populates="cv")


class KandoApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_applications"

    kando_application_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    kando_candidate_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kando_cv_id: Mapped[int | None] = mapped_column(Integer)
    kando_job_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kando_hire_step_id: Mapped[int | None] = mapped_column(Integer)
    kando_status_id: Mapped[int | None] = mapped_column(Integer)
    source_name: Mapped[str | None] = mapped_column(String(255))
    raw_payload_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_raw_payloads.id"),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class KandoCvWorkExperience(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_cv_work_experiences"

    kando_cv_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cv_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_cvs.id", ondelete="CASCADE"),
    )
    title: Mapped[str | None] = mapped_column(String(255))
    company_name: Mapped[str | None] = mapped_column(String(255))
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    cv: Mapped[KandoCv | None] = relationship(back_populates="work_experiences")


class KandoCvUniversityDegree(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_cv_university_degrees"

    kando_cv_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cv_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_cvs.id", ondelete="CASCADE"),
    )
    degree_name: Mapped[str | None] = mapped_column(String(255))
    university_name: Mapped[str | None] = mapped_column(String(255))
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    cv: Mapped[KandoCv | None] = relationship(back_populates="university_degrees")


class KandoCvLanguageSkill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_cv_language_skills"

    kando_cv_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cv_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("kando_cvs.id", ondelete="CASCADE"),
    )
    language_id: Mapped[int | None] = mapped_column(Integer)
    skill_level_id: Mapped[int | None] = mapped_column(Integer)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    cv: Mapped[KandoCv | None] = relationship(back_populates="language_skills")


class KandoBaseDataCache(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kando_base_data_cache"
    __table_args__ = (UniqueConstraint("data_type", "external_id", name="uq_kando_base_data_type_id"),)

    data_type: Mapped[str] = mapped_column(String(120), nullable=False)
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

