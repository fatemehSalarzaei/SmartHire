# Task 01 — Backend Foundation

## Goal

Implement FastAPI backend foundation, config, DB session, logging and Persian error contract.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/08-backend/backend-architecture.md`
- `docs/03-api/error-contract.md`
- `docs/03-api/fa-api-error-messages.md`

## Allowed files/directories

- `backend/`

## Forbidden changes

- Do not implement Kando write calls.
- Do not skip Persian message_fa.
- Do not implement domain decisions yet.

## Implementation tasks

1. Create FastAPI app.
2. Add settings via pydantic-settings.
3. Add request_id middleware.
4. Add global exception handlers.
5. Add health endpoint.
6. Add standard response helpers.

## Required tests/checks

- pytest backend/tests
- call health endpoint

## Acceptance criteria

- All errors follow contract.
- Health endpoint works.
- Persian error examples tested.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
