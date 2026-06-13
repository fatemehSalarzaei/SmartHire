# Task 10 — Internal API

## Goal

Implement internal API endpoints for jobs, rulesets, applications, runs, AI analysis, notes and admin retry.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/03-api/internal-openapi.yaml`
- `docs/03-api/api-design-rules.md`
- `docs/03-api/pagination-filter-sort-contract.md`

## Allowed files/directories

- `backend/app/api/v1/`
- `backend/app/schemas/`
- `backend/tests/`

## Forbidden changes

- Do not bypass service layer.
- Do not return English-only errors.
- Do not add unpaginated lists.

## Implementation tasks

1. Implement endpoints.
2. Add schemas.
3. Add pagination/filter/sort.
4. Add RBAC.
5. Add audit for mutations.
6. Add API tests.

## Required tests/checks

- pytest API tests

## Acceptance criteria

- All endpoints follow response contract.
- Pagination works.
- Persian errors returned.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
