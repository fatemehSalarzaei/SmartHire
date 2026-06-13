# Task 04 — Kando Read-only Integration

## Goal

Implement Kando client and sync service with strict read-only allowlist, retry, pagination and raw payload persistence.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/02-integrations/kando-api-contract.md`
- `docs/02-integrations/kando-readonly-boundary.md`
- `docs/02-integrations/kando-pagination-and-retry.md`
- `docs/02-integrations/kando-field-mapping.md`

## Allowed files/directories

- `backend/app/services/kando_client.py`
- `backend/app/services/kando_sync_service.py`
- `backend/app/workers/sync_tasks.py`
- `backend/tests/`

## Forbidden changes

- Do not add POST/PUT/PATCH/DELETE to Kando.
- Do not expose API key in logs.

## Implementation tasks

1. Create allowlisted GET methods.
2. Implement pagination.
3. Implement retry/backoff.
4. Persist raw payloads.
5. Normalize BaseData/jobs/applications enough for fixtures.

## Required tests/checks

- pytest Kando client tests with mocked responses
- test no non-GET Kando methods exist

## Acceptance criteria

- Kando client is read-only.
- Retry and pagination tested.
- Persian errors mapped.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
