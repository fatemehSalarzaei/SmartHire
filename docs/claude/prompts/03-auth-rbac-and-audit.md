# Task 03 — Auth, RBAC and Audit

## Goal

Implement authentication, role-based permissions and immutable audit foundation.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/10-security/permission-matrix.md`
- `docs/10-security/audit-policy.md`
- `docs/05-contracts/audit-log-contract.md`

## Allowed files/directories

- `backend/app/core/`
- `backend/app/api/v1/auth.py`
- `backend/app/services/audit_service.py`
- `backend/app/models/`

## Forbidden changes

- Do not expose sensitive data.
- Do not allow SQLAdmin to non-admin users.

## Implementation tasks

1. Implement JWT auth.
2. Implement current user dependency.
3. Implement permission checks.
4. Implement audit service.
5. Add tests for permission denied.

## Required tests/checks

- pytest auth/rbac/audit tests

## Acceptance criteria

- Protected routes enforce auth.
- Permission denied uses Persian message.
- Audit records created.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
