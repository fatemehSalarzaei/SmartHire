# Task 13 — Tests and Fixtures

## Goal

Expand fixture and golden-output coverage across backend and frontend.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/11-quality/test-strategy.md`
- `docs/11-quality/fixture-strategy.md`
- `tests/fixtures/`

## Allowed files/directories

- `tests/fixtures/`
- `backend/tests/`
- `frontend/tests/`

## Forbidden changes

- Do not use real candidate data.

## Implementation tasks

1. Add test fixtures.
2. Add expected outputs.
3. Add golden tests.
4. Add API error tests.
5. Add frontend state tests.

## Required tests/checks

- pytest
- npm test

## Acceptance criteria

- Golden tests deterministic.
- Expected outputs documented.
- No real PII.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
