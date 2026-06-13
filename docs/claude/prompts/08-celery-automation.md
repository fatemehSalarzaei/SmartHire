# Task 08 — Celery Automation

## Goal

Implement worker pipeline and schedules for automatic sync, AI, screening, ranking and notes.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/01-architecture/async-pipeline.md`
- `docs/08-backend/celery-tasks-and-queues.md`
- `docs/13-operations/scheduled-jobs.md`

## Allowed files/directories

- `backend/app/workers/`
- `backend/app/services/`

## Forbidden changes

- Do not expose HR manual daily screening.
- Do not create non-idempotent tasks.

## Implementation tasks

1. Create Celery app.
2. Define queues.
3. Define Beat schedule.
4. Chain pipeline tasks.
5. Add idempotency checks.
6. Record task logs/errors.

## Required tests/checks

- pytest worker tests

## Acceptance criteria

- Automatic pipeline exists.
- Tasks idempotent.
- Retry policy implemented.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
