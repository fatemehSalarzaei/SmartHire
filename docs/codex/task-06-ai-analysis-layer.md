# Task 06 — AI Analysis Layer

## Purpose

Task 06 adds an AI-assisted resume analysis layer for SmartHire. The layer consumes canonical snapshots produced by Task 05, sends only sanitized structured data to an LLM provider abstraction, validates strict JSON output, and persists AI run/result records.

AI output is advisory only. It does not make final hiring, screening, rejection, or ranking decisions.

## Files added or changed

### Services

- `backend/app/services/llm_client.py`
  - Defines the LLM provider abstraction.
  - Provides a disabled safe default provider.
  - Provides a minimal HTTP JSON provider for future production wiring.
  - Normalizes provider errors into retryable/non-retryable failure handling.

- `backend/app/services/prompt_builder.py`
  - Builds prompt version `resume-analysis-v1`.
  - Produces deterministic sanitized AI input.
  - Removes contact data, secrets, tokens, raw payload fields, and snapshot hash from AI input.
  - Produces stable `sha256:` input hashes.

- `backend/app/services/ai_analysis_service.py`
  - Validates AI JSON output with Pydantic schemas.
  - Persists `AIAnalysisRun` and `AIAnalysisResult`.
  - Stores Persian fallback errors for unavailable AI and invalid schema.
  - Allows one schema repair attempt.
  - Marks normalized AI signals as advisory only.

### Worker

- `backend/app/workers/ai_analysis_tasks.py`
  - Adds Celery task `ai.analyze_screening_application`.
  - Loads a screening application snapshot and runs the AI analysis service.

- `backend/app/workers/celery_app.py`
  - Imports `ai_analysis_tasks` so the configured Celery app registers the task at worker startup.

### Tests

- `backend/tests/test_ai_analysis_service.py`
  - Tests prompt sanitization.
  - Tests valid AI output persistence.
  - Tests one repair attempt for invalid JSON/schema.
  - Tests invalid output is not used.
  - Tests AI unavailable fallback behavior.
  - Tests Celery task registration.

## Behavior

The AI layer follows this lifecycle:

1. Receive canonical application snapshot.
2. Sanitize snapshot into AI-safe input.
3. Build versioned prompt.
4. Call LLM provider abstraction.
5. Parse and validate strict JSON output.
6. Persist successful validated output as advisory AI signals.
7. Persist failure state with Persian error message when AI is unavailable or schema-invalid.

## Guardrails

- No phone, email, exact address, raw payload, API key, password, token, or authorization header is sent to AI.
- AI output is never used as a hard reject/pass decision.
- AI output is never accepted as free-form text.
- Invalid AI output creates a failed run and no result row.
- AI failure does not stop structured screening by default.
- The Celery task only wraps AI analysis and does not execute Rule Engine or Ranking Engine logic.

## Output contract

Validated AI output must include:

- `summary_fa`
- `related_experience`
- `positive_signals`
- `negative_signals`
- `ambiguities`
- `suggested_score_reasons`

The persisted normalized signals include `advisory_only: true` to make the downstream boundary explicit.
