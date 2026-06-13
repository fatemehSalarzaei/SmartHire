# AGENTS.md — SmartHire Codex Guide

## Project identity

This repository implements **SmartHire / Kando ATS Screening & Ranking — Production-Ready Phase 1**.

The project is a small-system, production-ready, modular-monolith implementation for fewer than 100 internal users. The main heavy workload is asynchronous resume analysis, screening, ranking, and Kando sync.

## Mandatory source order

When instructions conflict, follow this order:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/claude/do-not-violate.md`
4. `docs/00-product/decision-invariants.md`
5. `docs/00-product/project-definition.md`
6. `docs/01-architecture/architecture-baseline.md`
7. Relevant domain/API/database/backend/frontend/quality documents under `docs/`
8. Existing code

## Required first read

Before implementing any task, read:

- `CLAUDE.md`
- `docs/claude/context-index.md`
- `docs/claude/do-not-violate.md`
- `docs/01-architecture/simplicity-constraints.md`
- The relevant task prompt under `docs/claude/prompts/`

## Hard invariants

- Kando is read-only in Phase 1.
- Do not create Kando write APIs.
- Do not call Kando POST, PUT, PATCH, or DELETE.
- Do not change candidate status, notes, tags, stages, or hiring steps inside Kando.
- SmartHire owns internal statuses, notes, scores, ranks, recruiter decisions, and audit logs.
- Screening and ranking must be automatic through workers.
- Manual screening/ranking endpoints are admin-only for reprocess/debug/retry.
- AI assists only; Rule Engine and Ranking Engine decide.
- AI output alone must never hard reject a candidate.
- Language evaluation uses Kando `languageId` and `skillLevelId`, not English percentage.
- All backend API errors must include Persian `message_fa`.
- All schema changes require Alembic migrations.
- Active RuleSets must not be edited in place. Create a new version.
- Sensitive data must be masked in logs, UI, admin views, exports, and AI inputs unless explicitly permitted.

## Architecture guardrails

Use:

- One FastAPI backend.
- One Next.js frontend.
- One PostgreSQL database.
- Redis for Celery broker/result backend.
- Celery workers and Beat for async/scheduled work.
- SQLAdmin only for technical `/admin`.

Do not introduce:

- Microservices.
- Kubernetes.
- Kafka.
- RabbitMQ.
- GraphQL.
- CQRS.
- Event sourcing.
- Service mesh.
- Generic plugin frameworks.
- Unneeded repository/factory/orchestration abstractions.

## Work style

Before implementation:

1. Identify the exact task prompt.
2. List allowed files and forbidden files from the prompt.
3. Inspect existing files before changing anything.
4. Implement the smallest complete vertical slice.
5. Add/update tests and fixtures.
6. Do not remove documentation unless explicitly instructed.

Before completion:

1. Run relevant backend tests if backend changed.
2. Run relevant frontend checks if frontend changed.
3. Run Alembic checks if models changed.
4. Report skipped tests honestly.
5. Do not claim success without evidence.

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

## Existing documentation note

This repository already contains Claude-oriented documentation. Treat it as project documentation, not Claude-only guidance. Do not rename or delete it unless explicitly asked.
