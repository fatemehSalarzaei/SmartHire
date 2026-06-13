from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import RecruiterDecision


class CreateRulesetRequest(BaseModel):
    kando_job_id: int = Field(ge=1)
    name: str = Field(min_length=2, max_length=255)
    version: int | None = Field(default=None, ge=1)
    default_missing_data_policy: str = "NEEDS_REVIEW"
    scoring_enabled: bool = True
    max_score: int = Field(default=100, ge=1, le=1000)
    ranking_scope: str = "JOB"
    groups: list[dict[str, Any]] = Field(default_factory=list)


class CreateNoteRequest(BaseModel):
    note_fa: str = Field(min_length=1, max_length=4000)
    note_type: str = "RECRUITER_NOTE"
    note_metadata_json: dict[str, Any] = Field(default_factory=dict)

    @field_validator("note_type")
    @classmethod
    def validate_note_type(cls, value: str) -> str:
        allowed = {"RECRUITER_NOTE", "SYSTEM_NOTE"}
        if value not in allowed:
            msg = "نوع یادداشت معتبر نیست."
            raise ValueError(msg)
        return value


class RecruiterDecisionRequest(BaseModel):
    decision: RecruiterDecision
    note_fa: str | None = Field(default=None, max_length=4000)
    reason_json: dict[str, Any] = Field(default_factory=dict)


class RetryRunRequest(BaseModel):
    force: bool = False


class AcceptedTaskResponse(BaseModel):
    task_id: str | None
    status: str = "accepted"
    message_fa: str


class IdPath(BaseModel):
    id: UUID
