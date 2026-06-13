from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SQLEnum

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import NoteType, RecruiterDecision
from app.models.mixins import TimestampMixin


class ScreeningNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "screening_notes"

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    note_type: Mapped[NoteType] = mapped_column(SQLEnum(NoteType, name="note_type"), nullable=False)
    note_fa: Mapped[str] = mapped_column(Text, nullable=False)
    author_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    note_metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class RecruiterDecisionRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "recruiter_decisions"

    screening_application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("screening_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    recruiter_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    decision: Mapped[RecruiterDecision] = mapped_column(
        SQLEnum(RecruiterDecision, name="recruiter_decision"),
        nullable=False,
    )
    note_fa: Mapped[str | None] = mapped_column(Text)
    reason_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
