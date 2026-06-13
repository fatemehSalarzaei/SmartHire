# Claude Task Breakdown

Each task has a matching prompt in `docs/claude/prompts/`.

| Task | Prompt | Goal | Human review level |
|---|---|---|---|
| 00 | `00-bootstrap-repository.md` | Repo, infra and scaffolding | low |
| 01 | `01-backend-foundation.md` | FastAPI, config, error contract | medium |
| 02 | `02-database-models-and-migrations.md` | SQLAlchemy models and Alembic | high |
| 03 | `03-auth-rbac-and-audit.md` | Auth, RBAC, audit | high |
| 04 | `04-kando-read-only-integration.md` | Read-only Kando sync | high |
| 05 | `05-snapshot-and-normalization.md` | Snapshot and normalization | medium |
| 06 | `06-ai-analysis-layer.md` | AI analysis with validation/fallback | high |
| 07 | `07-rule-engine-and-ranking-engine.md` | Rule and Ranking engines | high |
| 08 | `08-celery-automation.md` | Celery tasks and schedules | high |
| 09 | `09-sqladmin.md` | SQLAdmin views and restrictions | medium |
| 10 | `10-internal-api.md` | API endpoints | high |
| 11 | `11-frontend-foundation.md` | Next.js foundation | medium |
| 12 | `12-frontend-pages.md` | HR pages and workflows | high |
| 13 | `13-tests-and-fixtures.md` | Golden fixture tests | high |
| 14 | `14-observability-security-and-hardening.md` | logs, metrics, masking | high |
| 15 | `15-final-review-and-release-readiness.md` | final production review | high |

## Rule

Do not skip tasks. If a task is partially completed, mark it partial and explain what remains.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
