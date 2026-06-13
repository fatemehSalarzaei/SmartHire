# Task 06 — AI Analysis Layer

## Goal

Implement AI-assisted analysis service with provider abstraction, prompt versioning, JSON validation and fallback.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/07-ai/ai-assisted-analysis-spec.md`
- `docs/07-ai/ai-output-schema.md`
- `docs/07-ai/ai-fallback-policy.md`
- `docs/15-compliance/ai-data-handling-policy.md`

## Allowed files/directories

- `backend/app/services/llm_client.py`
- `backend/app/services/prompt_builder.py`
- `backend/app/services/ai_analysis_service.py`
- `backend/app/workers/ai_analysis_tasks.py`
- `backend/tests/`

## Forbidden changes

- Do not make AI final decision.
- Do not send phone/email/API key/raw payload to AI.
- Do not accept free-form output.

## Implementation tasks

1. Create provider abstraction.
2. Build sanitized AI input.
3. Validate JSON output.
4. Persist AI run/result.
5. Implement fallback.
6. Add tests for valid/invalid AI output.

## Required tests/checks

- pytest AI analysis tests

## Acceptance criteria

- Invalid AI output not used.
- AI failure does not stop screening by default.
- Persian AI errors stored.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
