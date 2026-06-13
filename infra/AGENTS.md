# infra/AGENTS.md — SmartHire Infrastructure Rules

## Scope

Infrastructure is Docker Compose based for Phase 1 production-ready deployment.

## Required documents

Before infra work, read:

- `docs/12-deployment/docker-compose-spec.md`
- `docs/12-deployment/deployment-plan.md`
- `docs/12-deployment/environment-variables.md`
- `docs/12-deployment/rollback-plan.md`
- `docs/13-operations/runbook.md`
- `docs/13-operations/backup-restore.md`
- `docs/13-operations/failure-recovery.md`
- `docs/14-performance/celery-worker-scaling.md`

## Rules

- Do not introduce Kubernetes.
- Do not introduce service mesh.
- Do not introduce Kafka or RabbitMQ.
- Do not commit secrets.
- Use `.env.example` for documented variables only.
- Keep deployment compatible with Docker Compose.
- Optimize worker concurrency and database indexes before adding infrastructure complexity.

## Checks

```bash
docker compose config
docker compose up -d --build
```
