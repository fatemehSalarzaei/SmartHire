# Task 14 — Observability, Security and Hardening

## Goal

Add production security, logging, metrics, masking, and operational hardening.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/13-operations/observability-spec.md`
- `docs/10-security/security-privacy.md`
- `docs/14-performance/performance-baseline.md`

## Allowed files/directories

- `backend/`
- `frontend/`
- `infra/`
- `docs/`

## Forbidden changes

- Do not expose secrets.
- Do not weaken RBAC.

## Implementation tasks

1. Add structured logs.
2. Add metrics hooks.
3. Add masking.
4. Add health checks.
5. Add performance indexes if needed.
6. Add security headers config.

## Required tests/checks

- security/masking tests
- health checks

## Acceptance criteria

- Logs masked.
- Metrics available.
- Security checks pass.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
