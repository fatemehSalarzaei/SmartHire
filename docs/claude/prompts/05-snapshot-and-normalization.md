# Task 05 — Snapshot and Normalization

## Goal

Implement canonical snapshot builder and normalization utilities.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/05-contracts/snapshot-contract.md`
- `docs/06-domain/normalization-spec.md`
- `docs/02-integrations/kando-field-mapping.md`

## Allowed files/directories

- `backend/app/services/snapshot_builder.py`
- `backend/app/services/normalization_service.py`
- `backend/tests/`
- `tests/fixtures/`

## Forbidden changes

- Do not make decisions here.
- Do not include API keys or raw payload in AI input.

## Implementation tasks

1. Build snapshot from normalized models.
2. Calculate deterministic hash.
3. Detect missing fields.
4. Normalize Persian/English text.
5. Add fixture tests.

## Required tests/checks

- pytest snapshot/normalization tests

## Acceptance criteria

- Snapshot matches contract.
- Hash stable.
- Missing field policy data captured.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
