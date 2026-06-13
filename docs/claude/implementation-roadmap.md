# Implementation Roadmap — Production-Ready Phase 1

## Phase 0 — Repository foundation
- Create monorepo structure.
- Add backend/frontend/infra scaffolding.
- Add env, Docker Compose, Makefile.
- Add CI skeleton.

## Phase 1 — Backend foundation
- FastAPI app.
- Config.
- DB session.
- Alembic.
- Error contract.
- Auth/RBAC foundation.
- Audit foundation.

## Phase 2 — Database models
- Kando cache models.
- RuleSet models.
- Screening/Ranking models.
- AI models.
- Notes/recruiter decisions.
- Indexes and constraints.

## Phase 3 — Kando integration
- Read-only client.
- Endpoint allowlist.
- Pagination/retry.
- Raw payload storage.
- BaseData/job/application sync.

## Phase 4 — Snapshot and normalization
- Snapshot contract.
- Normalization service.
- Snapshot hash.
- Missing-field detection.

## Phase 5 — AI Analysis
- LLM client abstraction.
- Prompt builder.
- JSON schema validation.
- AI run/result persistence.
- Fallback policy.

## Phase 6 — Rule Engine and Ranking Engine
- Deterministic rule evaluation.
- Score and rank.
- Fixture-based golden tests.

## Phase 7 — Automatic pipeline
- Celery app.
- Queues.
- Beat schedules.
- Task idempotency.
- Run logs and retry.

## Phase 8 — SQLAdmin
- Mount SQLAdmin.
- Admin auth.
- Views.
- Read-only restrictions.
- Masking and audit.

## Phase 9 — Internal API
- Jobs.
- Rulesets.
- Applications.
- AI analysis.
- Notes.
- Runs/retry.
- Pagination/filter/sort.

## Phase 10 — Frontend foundation
- Next.js app.
- Auth.
- API client.
- Layout.
- Permission helpers.

## Phase 11 — Frontend workflows
- Jobs.
- Rule Builder.
- Applications list.
- Application detail.
- AI Analysis view.
- Notes and recruiter decisions.

## Phase 12 — Hardening
- CI gates.
- Security review.
- Observability.
- Backups.
- Production checklist.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
