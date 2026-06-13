# Task 09 — SQLAdmin

## Goal

Mount SQLAdmin on /admin with RBAC, read-only restrictions, masking and audit.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/08-backend/sqladmin-spec.md`
- `docs/10-security/permission-matrix.md`

## Allowed files/directories

- `backend/app/admin/`
- `backend/app/main.py`
- `backend/tests/`

## Forbidden changes

- Do not let HR roles access /admin.
- Do not make Kando cache editable.
- Do not show full API keys.

## Implementation tasks

1. Mount SQLAdmin.
2. Add admin auth.
3. Create views.
4. Apply read-only/editable boundaries.
5. Mask sensitive values.
6. Audit sensitive changes.

## Required tests/checks

- pytest SQLAdmin access/masking tests

## Acceptance criteria

- Only technical roles access /admin.
- Read-only models protected.
- Sensitive values masked.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
