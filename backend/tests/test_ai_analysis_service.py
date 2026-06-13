import json
from uuid import UUID

from app.models.ai import AIAnalysisResult, AIAnalysisRun
from app.models.enums import AIAnalysisStatus
from app.services.ai_analysis_service import (
    AI_ANALYSIS_UNAVAILABLE_CODE,
    AI_SCHEMA_VALIDATION_FAILED_CODE,
    AIAnalysisService,
)
from app.services.llm_client import LLMClient, LLMProviderError, LLMRequest, LLMResponse
from app.services.prompt_builder import PromptBuilder
from app.workers.celery_app import celery_app


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.flushed = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    def flush(self) -> None:
        self.flushed += 1


class FakeProvider:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, responses: list[str] | None = None, fail: bool = False) -> None:
        self.responses = responses or []
        self.fail = fail
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if self.fail:
            raise LLMProviderError()
        return LLMResponse(
            content=self.responses.pop(0),
            provider=self.provider_name,
            model_name=self.model_name,
        )


def _snapshot() -> dict:
    return {
        "snapshot_version": "v1",
        "snapshot_hash": "sha256:abc",
        "kando": {"application_id": 1001},
        "job": {"title": "Customer Support", "requirements": "CRM experience"},
        "candidate": {
            "full_name": "Candidate",
            "email": "candidate@example.com",
            "mobile": "09123456789",
        },
        "cv": {"about_me": "Customer support specialist", "skills": ["CRM"]},
        "application_sources": [{"cover_letter": "I helped customers", "cv_id": 9001}],
        "work_experiences": [
            {
                "role_title": "Customer Support Specialist",
                "company_name": "Example",
                "description": "Handled tickets",
                "duration_months": 24,
            },
        ],
        "education": [],
        "language_skills": [{"language": "English", "level": "Advanced"}],
        "software_skills": [],
        "missing_fields": [],
        "metadata": {"source": "normalized_kando_tables"},
    }


def _valid_output() -> str:
    return json.dumps(
        {
            "summary_fa": "کاندیدا سابقه مرتبط در پشتیبانی مشتری دارد.",
            "related_experience": {
                "is_related": True,
                "confidence": 0.82,
                "matched_categories": ["customer_support"],
                "evidence": ["Customer Support Specialist"],
            },
            "positive_signals": [
                {
                    "code": "SUPPORT_EXPERIENCE",
                    "label_fa": "سابقه پشتیبانی مشتری",
                    "confidence": 0.86,
                    "evidence": "Customer Support Specialist",
                },
            ],
            "negative_signals": [],
            "ambiguities": [
                {
                    "code": "UNCLEAR_DURATION",
                    "label_fa": "ابهام در مدت سابقه",
                    "severity": "LOW",
                },
            ],
            "suggested_score_reasons": [
                {
                    "reason_code": "RELATED_SUPPORT_EXPERIENCE",
                    "suggested_score_delta": 15,
                    "explanation_fa": "سابقه مرتبط با پشتیبانی مشتری شناسایی شد.",
                },
            ],
        },
        ensure_ascii=False,
    )


def test_prompt_builder_sanitizes_contact_raw_payload_and_secrets() -> None:
    prompt = PromptBuilder().build_resume_analysis_prompt(snapshot=_snapshot())
    serialized = json.dumps(prompt.sanitized_input, ensure_ascii=False)

    assert prompt.prompt_version == "resume-analysis-v1"
    assert prompt.output_schema_version == "ai-output-v1"
    assert prompt.input_hash.startswith("sha256:")
    assert "candidate@example.com" not in serialized
    assert "09123456789" not in serialized
    assert "raw_payload" not in serialized
    assert "api_key" not in serialized.lower()
    assert "Customer Support" in prompt.user_message


def test_valid_ai_output_is_persisted_as_advisory_signals_only() -> None:
    db = FakeDb()
    provider = FakeProvider([_valid_output()])

    outcome = AIAnalysisService(db, llm_client=LLMClient(provider)).analyze_snapshot(
        screening_application_id=UUID("11111111-1111-1111-1111-111111111111"),
        snapshot=_snapshot(),
    )

    assert outcome.used_output is True
    assert outcome.error_code is None
    assert outcome.run.status == AIAnalysisStatus.SUCCEEDED
    assert isinstance(outcome.result, AIAnalysisResult)
    assert outcome.result.output_json["summary_fa"].startswith("کاندیدا")
    assert outcome.result.normalized_signals_json["advisory_only"] is True
    assert outcome.result.confidence == 0.82
    assert any(isinstance(item, AIAnalysisRun) for item in db.added)
    assert any(isinstance(item, AIAnalysisResult) for item in db.added)


def test_invalid_ai_output_is_repaired_once_when_second_response_is_valid() -> None:
    db = FakeDb()
    provider = FakeProvider(["not-json", _valid_output()])

    outcome = AIAnalysisService(db, llm_client=LLMClient(provider)).analyze_snapshot(
        screening_application_id=UUID("22222222-2222-2222-2222-222222222222"),
        snapshot=_snapshot(),
    )

    assert outcome.used_output is True
    assert outcome.run.status == AIAnalysisStatus.SUCCEEDED
    assert outcome.run.retry_count == 1
    assert len(provider.requests) == 2


def test_invalid_ai_output_is_not_used_after_repair_fails() -> None:
    db = FakeDb()
    provider = FakeProvider(["not-json", json.dumps({"summary_fa": "ناقص"}, ensure_ascii=False)])

    outcome = AIAnalysisService(db, llm_client=LLMClient(provider)).analyze_snapshot(
        screening_application_id=UUID("33333333-3333-3333-3333-333333333333"),
        snapshot=_snapshot(),
    )

    assert outcome.used_output is False
    assert outcome.result is None
    assert outcome.run.status == AIAnalysisStatus.FAILED_SCHEMA_VALIDATION
    assert outcome.error_code == AI_SCHEMA_VALIDATION_FAILED_CODE
    assert outcome.message_fa == (
        "خروجی هوش مصنوعی با ساختار مورد انتظار سامانه سازگار نبود و در تصمیم نهایی استفاده نشد."
    )
    assert not any(isinstance(item, AIAnalysisResult) for item in db.added)


def test_unknown_signal_code_requires_custom_prefix() -> None:
    payload = json.loads(_valid_output())
    payload["positive_signals"][0]["code"] = "UNLISTED_SIGNAL"
    db = FakeDb()
    invalid_response = json.dumps(payload, ensure_ascii=False)
    provider = FakeProvider([invalid_response, invalid_response])

    outcome = AIAnalysisService(db, llm_client=LLMClient(provider)).analyze_snapshot(
        screening_application_id=UUID("44444444-4444-4444-4444-444444444444"),
        snapshot=_snapshot(),
    )

    assert outcome.used_output is False
    assert outcome.error_code == AI_SCHEMA_VALIDATION_FAILED_CODE


def test_ai_unavailable_is_persisted_as_failed_run_without_raising() -> None:
    db = FakeDb()
    provider = FakeProvider(fail=True)

    outcome = AIAnalysisService(db, llm_client=LLMClient(provider)).analyze_snapshot(
        screening_application_id=UUID("55555555-5555-5555-5555-555555555555"),
        snapshot=_snapshot(),
    )

    assert outcome.used_output is False
    assert outcome.result is None
    assert outcome.run.status == AIAnalysisStatus.FAILED
    assert outcome.error_code == AI_ANALYSIS_UNAVAILABLE_CODE
    assert outcome.retryable is True
    assert outcome.message_fa == (
        "تحلیل هوش مصنوعی در حال حاضر در دسترس نیست. رزومه با قوانین ساختاریافته بررسی شد."
    )


def test_ai_analysis_task_is_registered_from_celery_app_startup() -> None:
    assert "ai.analyze_screening_application" in celery_app.tasks
