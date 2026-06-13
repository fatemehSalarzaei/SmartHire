# Task 07 — Rule Engine and Ranking Engine

## Summary

Task 07 adds the deterministic Rule Engine and Ranking Engine for SmartHire Phase 1. These services evaluate canonical application snapshots and RuleSet JSON/DB-shaped rule data without calling Kando, AI providers, APIs, or frontend code.

## Files added

- `backend/app/services/rule_engine.py`
- `backend/app/services/ranking_engine.py`
- `backend/tests/test_rule_engine.py`
- `backend/tests/test_ranking_engine.py`
- `tests/fixtures/snapshots/application_snapshot_rejected.json`

## Rule Engine behavior

The Rule Engine:

- Evaluates rules as data, not hardcoded customer-support Python logic.
- Supports deterministic operators used by the current RuleSet fixtures.
- Applies missing data policy.
- Returns `UNSUPPORTED_SOURCE` when structured CV data is unavailable.
- Returns `NEEDS_HUMAN_REVIEW` for missing critical data by default.
- Returns `SMART_REJECTED` only from deterministic configured rules.
- Returns `SMART_NOT_REJECTED` when deterministic gates pass.
- Blocks AI-targeted hard reject rules unless explicitly allowed.

AI signals may be evaluated for configured scoring/review rules, but AI alone is not allowed to hard reject a candidate.

## Ranking Engine behavior

The Ranking Engine:

- Computes deterministic priority scores from configured scoring rules.
- Normalizes scores to `0-100`.
- Assigns priority buckets:
  - `HIGH` for scores >= 75
  - `MEDIUM` for scores >= 50 and < 75
  - `LOW` for scores < 50
  - `REVIEW_UNKNOWN` when required data is insufficient
- Ranks applications per job by score, gate pass count, positive reason count, missing-field count, and deterministic timestamp/application-id tie breakers.
- Does not rank unsupported or missing-data unknown applications into the recruiter priority queue.

## Boundaries preserved

This task does not add:

- Kando write behavior
- AI provider calls
- AI final decisions
- RuleSet editing
- API endpoints
- Celery automation pipeline
- SQLAdmin
- frontend changes
- database schema changes

## Test coverage

The tests cover:

- Golden screening decisions from fixtures.
- Missing language defaults to human review, not hard reject.
- Unsupported structured CV source handling.
- AI-only hard reject prevention.
- Golden ranking output for valid and missing-data snapshots.
- AI scoring bonus as advisory-only scoring input.
- Per-job deterministic rank ordering.

## Notes

Task 07 intentionally keeps persistence out of the service layer. Persisting `ScreeningDecision`, `ScreeningScore`, and `RankingResult` rows belongs to the worker automation and orchestration layer in later tasks.
