# Task 00 — Bootstrap Repository

## Goal

Create the production-ready monorepo scaffolding without implementing business logic.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/01-architecture/architecture-baseline.md`
- `docs/12-deployment/docker-compose-spec.md`

## Allowed files/directories

- `.`
- `backend/`
- `frontend/`
- `infra/`
- `docs/`

## Forbidden changes

- Do not implement business logic.
- Do not remove docs.
- Do not add real secrets.

## Implementation tasks

1. Create backend/frontend/infra directory skeleton.
2. Add Dockerfiles as placeholders or working minimal images.
3. Ensure .env.example matches docs.
4. Add README run instructions.

## Required tests/checks

- docker compose config
- basic file tree check

## Acceptance criteria

- Repository structure exists.
- No secret committed.
- Docker Compose config validates.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
