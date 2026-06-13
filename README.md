# SmartHire Claude Implementation Pack

This repository pack is the **production-ready Phase 1 implementation guide** for SmartHire / Kando ATS Screening & Ranking.

It is designed for Claude Code / Claude Agent implementation with minimal human review. It contains:

- Product decisions and invariants.
- Architecture contracts.
- Kando read-only API contracts.
- Internal API contracts.
- Database model and migration policy.
- Rule Engine, Ranking Engine, AI Analysis, and automatic pipeline specs.
- Backend and frontend implementation rules.
- Production quality gates.
- Fixtures and golden expected outputs.
- Step-by-step Claude task prompts.

## Source of truth

1. `CLAUDE.md`
2. `docs/claude/context-index.md`
3. `docs/00-product/decision-invariants.md`
4. `docs/00-product/project-definition.md`
5. `docs/01-architecture/architecture-baseline.md`
6. `docs/05-contracts/snapshot-contract.md`
7. `docs/06-domain/screening-pipeline-spec.md`
8. `docs/claude/do-not-violate.md`

## Production-ready Phase 1 principles

- Kando is read-only.
- SmartHire stores internal statuses, notes, scores, ranks, decisions, and audit data.
- Screening and ranking are automatic and worker-based.
- Manual execution is admin-only reprocess/debug/retry.
- AI is assistive only. Rule Engine and Ranking Engine are the auditable decision source.
- Backend API errors must include Persian user-facing messages.
- Every schema change requires Alembic migration.
- Active RuleSets must not be edited in place; create a new version.
- Sensitive data must be masked in logs and restricted by RBAC.


## Small-system production stance

This project is production-ready Phase 1 for fewer than 100 internal users. Keep it modular-monolith-first. The main heavy workload is background resume analysis, so capacity should be handled through Celery scheduling, queue concurrency, and database/index optimization—not through microservices or Kubernetes.

## Local Bootstrap

Task 00 provides only repository scaffolding. It does not implement SmartHire business logic, Kando integration, authentication, screening, ranking, AI analysis, or SQLAdmin configuration.

### Prerequisites

- Docker and Docker Compose.
- A local `.env` copied from `.env.example`.

### Setup

```bash
cp .env.example .env
docker compose config
docker compose up --build
```

Services exposed locally:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Backend health check: `http://localhost:8000/healthz`
- Nginx reverse proxy: `http://localhost:8080`

### Compose Services

The local Compose stack contains:

- `backend`: FastAPI application scaffold.
- `frontend`: Next.js application scaffold.
- `postgres`: PostgreSQL database.
- `redis`: Celery broker/result backend.
- `celery_worker`: background worker using the backend image.
- `celery_beat`: scheduler using the backend image.
- `nginx`: reverse proxy.

### Safety Notes

- Kando is read-only in Phase 1.
- Do not commit real Kando, AI, JWT, database, or observability secrets.
- Keep `.env.example` limited to placeholders and safe local defaults.
- Use Docker Compose and the modular monolith structure; do not add microservices or extra infrastructure for Task 00.
