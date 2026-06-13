# CLAUDE.md — SmartHire Implementation Rules

You are implementing **SmartHire Kando ATS Screening & Ranking — Production-Ready Phase 1**.

## Mandatory source order

When instructions conflict, follow this order:

1. `CLAUDE.md`
2. `docs/claude/do-not-violate.md`
3. `docs/00-product/decision-invariants.md`
4. `docs/00-product/project-definition.md`
5. `docs/01-architecture/architecture-baseline.md`
6. Domain, API, database, backend, frontend and quality documents under `docs/`
7. Existing code

## Hard invariants

- Kando is read-only in Phase 1.
- Do not call or invent Kando write APIs.
- Do not change status, note, tag, or stage inside Kando.
- All SmartHire statuses and notes are internal.
- Screening/ranking must be automatic through scheduled/event-driven workers.
- Manual screening/ranking endpoints are only for admin reprocess/debug/retry.
- Language evaluation uses Kando skill level, not percentage.
- AI assists only; Rule Engine and Ranking Engine decide.
- AI output alone must never hard reject a candidate.
- RuleSets must be configurable and versioned; do not hardcode customer-support rules in Python.
- All backend API errors must include Persian `message_fa`.
- All schema changes require Alembic migrations.
- Sensitive data must be masked in logs, admin UI, and exports unless the role has permission.
- `/admin` is SQLAdmin for technical users only; HR workflow belongs in the Next.js panel.

## Simplicity and scale guardrails

This is a **production-ready small-system implementation**, not an enterprise distributed platform.

Target operating assumptions:

- Internal users are fewer than 100.
- Concurrent UI users are low.
- The main workload is asynchronous resume analysis, not high-volume web traffic.
- The correct architecture is a modular monolith with background workers.
- Production-ready means secure, tested, observable, auditable, and recoverable; it does **not** mean microservices or Kubernetes.

Claude must keep the implementation simple:

- Use one FastAPI backend application.
- Use one Next.js frontend application.
- Use one PostgreSQL database.
- Use Redis for Celery broker/result backend.
- Use Celery workers for sync, AI analysis, screening, and ranking.
- Keep queue names logical; do not introduce separate deployable services unless explicitly requested.
- Do not introduce Kubernetes, service mesh, event bus, Kafka, RabbitMQ, multi-tenant infrastructure, CQRS, event sourcing, GraphQL, or separate microservices.
- Do not add abstractions, factories, repositories, plugins, or orchestration layers unless a current requirement needs them.
- Prefer clear service modules, explicit SQLAlchemy models, Pydantic schemas, deterministic functions, and fixture-based tests.
- Optimize database indexes and Celery concurrency before proposing infrastructure scaling.

## Required work style

Before implementation:
- Read `docs/claude/context-index.md`.
- Read the specific task prompt under `docs/claude/prompts/`.
- Identify allowed files and forbidden files in the task prompt.
- Implement the smallest complete vertical slice for the task.
- Add or update tests and fixtures.

Before reporting completion:
- Run backend tests if backend changed.
- Run frontend checks if frontend changed.
- Run migration checks if models changed.
- Summarize changed files, tests run, skipped tests, and risks.

## Completion report format

Return:

```text
STATUS: completed / partial / blocked
FILES_CHANGED:
- path
TESTS_RUN:
- command + result
RISKS:
- ...
NEXT_RECOMMENDED_TASK:
- ...
```

Do not claim success without test evidence.
