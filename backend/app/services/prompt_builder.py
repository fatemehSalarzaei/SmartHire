from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

PROMPT_VERSION = "resume-analysis-v1"
AI_OUTPUT_SCHEMA_VERSION = "ai-output-v1"
SNAPSHOT_INPUT_SCHEMA_VERSION = "snapshot-v1"

SYSTEM_MESSAGE = """You analyze structured resume data for a hiring assistant.
Return only valid JSON matching the schema.
Do not make final hiring decisions.
Do not invent facts.
Do not infer sensitive attributes.
Use only evidence in the input.
Write summaries and labels in Persian."""

CONTACT_OR_SECRET_KEYS = {
    "email",
    "mobile",
    "phone",
    "telephone",
    "address",
    "exact_address",
    "api_key",
    "apikey",
    "companyapikey",
    "authorization",
    "token",
    "password",
    "password_hash",
    "raw_payload",
    "raw_payload_json",
    "payload_json",
}

ALLOWED_SNAPSHOT_SECTIONS = {
    "job",
    "cv",
    "application_sources",
    "work_experiences",
    "education",
    "language_skills",
    "software_skills",
    "missing_fields",
    "metadata",
}


@dataclass(frozen=True)
class BuiltPrompt:
    system_message: str
    user_message: str
    prompt_version: str
    output_schema_version: str
    sanitized_input: dict[str, Any]
    input_hash: str


class PromptBuilder:
    def build_resume_analysis_prompt(
        self,
        *,
        snapshot: dict[str, Any],
        ruleset_summary: dict[str, Any] | None = None,
    ) -> BuiltPrompt:
        sanitized_input = {
            "input_schema_version": SNAPSHOT_INPUT_SCHEMA_VERSION,
            "job": sanitize_for_ai(snapshot.get("job") or {}),
            "ruleset_summary": sanitize_for_ai(ruleset_summary or {}),
            "candidate_cv": sanitize_for_ai(
                {
                    key: snapshot.get(key)
                    for key in ALLOWED_SNAPSHOT_SECTIONS
                    if key != "job"
                },
            ),
        }
        input_hash = stable_json_hash(sanitized_input)
        user_message = (
            "Job:\n"
            f"{_json(sanitized_input['job'])}\n\n"
            "Ruleset summary:\n"
            f"{_json(sanitized_input['ruleset_summary'])}\n\n"
            "Candidate CV structured data:\n"
            f"{_json(sanitized_input['candidate_cv'])}\n\n"
            "Return JSON with: summary_fa, related_experience, positive_signals, "
            "negative_signals, ambiguities, suggested_score_reasons."
        )
        return BuiltPrompt(
            system_message=SYSTEM_MESSAGE,
            user_message=user_message,
            prompt_version=PROMPT_VERSION,
            output_schema_version=AI_OUTPUT_SCHEMA_VERSION,
            sanitized_input=sanitized_input,
            input_hash=input_hash,
        )


def sanitize_for_ai(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized_key = str(key).replace("_", "").replace("-", "").lower()
            if normalized_key in CONTACT_OR_SECRET_KEYS:
                continue
            if key in {"snapshot_hash", "kando"}:
                continue
            sanitized[key] = sanitize_for_ai(nested_value)
        return sanitized
    if isinstance(value, list):
        return [sanitize_for_ai(item) for item in value]
    return value


def stable_json_hash(value: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
