from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai import AIAnalysisResult, AIAnalysisRun
from app.models.enums import AIAnalysisStatus
from app.models.screening import ScreeningApplication
from app.services.llm_client import LLMClient, LLMProviderError, LLMRequest
from app.services.prompt_builder import PromptBuilder

AI_SCHEMA_VALIDATION_FAILED_CODE = "AI_SCHEMA_VALIDATION_FAILED"
AI_SCHEMA_VALIDATION_FAILED_MESSAGE_FA = (
    "خروجی هوش مصنوعی با ساختار مورد انتظار سامانه سازگار نبود و در تصمیم نهایی استفاده نشد."
)
AI_ANALYSIS_UNAVAILABLE_CODE = "AI_ANALYSIS_UNAVAILABLE"
AI_ANALYSIS_UNAVAILABLE_MESSAGE_FA = (
    "تحلیل هوش مصنوعی در حال حاضر در دسترس نیست. رزومه با قوانین ساختاریافته بررسی شد."
)

_ALLOWED_SIGNAL_CODES = {
    "SUPPORT_EXPERIENCE",
    "SALES_EXPERIENCE",
    "RELATED_EXPERIENCE",
    "LANGUAGE_SKILL",
    "CRM_SKILL",
    "SHORT_TENURE",
    "MISSING_DURATION",
}


class RelatedExperienceOutput(BaseModel):
    is_related: bool
    confidence: float = Field(ge=0.0, le=1.0)
    matched_categories: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class SignalOutput(BaseModel):
    code: str
    label_fa: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str

    @field_validator("code")
    @classmethod
    def known_or_custom_code(cls, value: str) -> str:
        if value in _ALLOWED_SIGNAL_CODES or value.startswith("CUSTOM_"):
            return value
        raise ValueError("unknown signal codes must start with CUSTOM_")


class AmbiguityOutput(BaseModel):
    code: str
    label_fa: str
    severity: str

    @field_validator("severity")
    @classmethod
    def valid_severity(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("severity must be LOW, MEDIUM, or HIGH")
        return normalized


class SuggestedScoreReasonOutput(BaseModel):
    reason_code: str
    suggested_score_delta: int
    explanation_fa: str


class AIResumeAnalysisOutput(BaseModel):
    summary_fa: str = Field(min_length=1, max_length=1200)
    related_experience: RelatedExperienceOutput
    positive_signals: list[SignalOutput] = Field(default_factory=list)
    negative_signals: list[SignalOutput] = Field(default_factory=list)
    ambiguities: list[AmbiguityOutput] = Field(default_factory=list)
    suggested_score_reasons: list[SuggestedScoreReasonOutput] = Field(default_factory=list)

    def normalized_signals(self) -> dict[str, Any]:
        return {
            "related_experience": self.related_experience.model_dump(mode="json"),
            "positive_signal_codes": [signal.code for signal in self.positive_signals],
            "negative_signal_codes": [signal.code for signal in self.negative_signals],
            "ambiguity_codes": [ambiguity.code for ambiguity in self.ambiguities],
            "suggested_reason_codes": [
                reason.reason_code for reason in self.suggested_score_reasons
            ],
            "advisory_only": True,
        }


@dataclass(frozen=True)
class AIAnalysisOutcome:
    run: AIAnalysisRun
    result: AIAnalysisResult | None
    used_output: bool
    error_code: str | None
    message_fa: str | None
    retryable: bool


class AIAnalysisService:
    def __init__(
        self,
        db: Session,
        *,
        llm_client: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.db = db
        self.llm_client = llm_client or LLMClient()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def analyze_snapshot(
        self,
        *,
        screening_application_id: UUID,
        snapshot: dict[str, Any],
        ruleset_id: UUID | None = None,
        ruleset_version: int | None = None,
        ruleset_summary: dict[str, Any] | None = None,
    ) -> AIAnalysisOutcome:
        prompt = self.prompt_builder.build_resume_analysis_prompt(
            snapshot=snapshot,
            ruleset_summary=ruleset_summary,
        )
        run = AIAnalysisRun(
            screening_application_id=screening_application_id,
            ruleset_id=ruleset_id,
            ruleset_version=ruleset_version,
            provider=self.llm_client.provider_name,
            model_name=self.llm_client.model_name,
            prompt_version=prompt.prompt_version,
            input_hash=prompt.input_hash,
            status=AIAnalysisStatus.RUNNING,
            retry_count=0,
        )
        _ensure_uuid(run)
        self.db.add(run)
        self.db.flush()

        request = LLMRequest(
            system_message=prompt.system_message,
            user_message=prompt.user_message,
            prompt_version=prompt.prompt_version,
        )
        try:
            response = self.llm_client.complete(request)
        except LLMProviderError as exc:
            return self._mark_failed(
                run,
                status=AIAnalysisStatus.FAILED,
                error_code=exc.code,
                message_fa=exc.message_fa,
                retryable=exc.retryable,
            )

        parsed = _parse_and_validate(response.content)
        if parsed is None:
            repair_request = LLMRequest(
                system_message=prompt.system_message,
                user_message=(
                    "The previous response was not valid JSON for the required schema. "
                    "Repair it once. Return only valid JSON.\n\n"
                    f"Original prompt input:\n{prompt.user_message}"
                ),
                prompt_version=prompt.prompt_version,
            )
            run.retry_count = 1
            try:
                response = self.llm_client.complete(repair_request)
            except LLMProviderError as exc:
                return self._mark_failed(
                    run,
                    status=AIAnalysisStatus.FAILED,
                    error_code=exc.code,
                    message_fa=exc.message_fa,
                    retryable=exc.retryable,
                )
            parsed = _parse_and_validate(response.content)

        if parsed is None:
            return self._mark_failed(
                run,
                status=AIAnalysisStatus.FAILED_SCHEMA_VALIDATION,
                error_code=AI_SCHEMA_VALIDATION_FAILED_CODE,
                message_fa=AI_SCHEMA_VALIDATION_FAILED_MESSAGE_FA,
                retryable=False,
            )

        output_json = parsed.model_dump(mode="json")
        result = AIAnalysisResult(
            ai_analysis_run_id=run.id,
            output_json=output_json,
            normalized_signals_json=parsed.normalized_signals(),
            confidence=parsed.related_experience.confidence,
        )
        _ensure_uuid(result)
        run.status = AIAnalysisStatus.SUCCEEDED
        run.error_code = None
        run.error_message_fa = None
        self.db.add(result)
        self.db.flush()
        return AIAnalysisOutcome(
            run=run,
            result=result,
            used_output=True,
            error_code=None,
            message_fa=None,
            retryable=False,
        )

    def analyze_screening_application(
        self,
        screening_application_id: UUID,
        *,
        ruleset_id: UUID | None = None,
        ruleset_version: int | None = None,
        ruleset_summary: dict[str, Any] | None = None,
    ) -> AIAnalysisOutcome:
        application = self.db.execute(
            select(ScreeningApplication).where(ScreeningApplication.id == screening_application_id),
        ).scalar_one_or_none()
        if application is None:
            raise ValueError(f"Screening application not found: {screening_application_id}")
        return self.analyze_snapshot(
            screening_application_id=screening_application_id,
            snapshot=application.raw_snapshot_json,
            ruleset_id=ruleset_id,
            ruleset_version=ruleset_version,
            ruleset_summary=ruleset_summary,
        )

    def _mark_failed(
        self,
        run: AIAnalysisRun,
        *,
        status: AIAnalysisStatus,
        error_code: str,
        message_fa: str,
        retryable: bool,
    ) -> AIAnalysisOutcome:
        run.status = status
        run.error_code = error_code
        run.error_message_fa = message_fa
        self.db.flush()
        return AIAnalysisOutcome(
            run=run,
            result=None,
            used_output=False,
            error_code=error_code,
            message_fa=message_fa,
            retryable=retryable,
        )


def _parse_and_validate(content: str) -> AIResumeAnalysisOutput | None:
    try:
        payload = json.loads(content)
        return AIResumeAnalysisOutput.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return None


def _ensure_uuid(instance: object) -> None:
    if getattr(instance, "id", None) is None:
        setattr(instance, "id", uuid4())
