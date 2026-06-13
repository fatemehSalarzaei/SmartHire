# Task 12 — Frontend Pages

## Goal

Implement HR pages for jobs, Rule Builder, application queues, details, AI analysis, notes and runs.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/09-frontend/page-specs.md`
- `docs/09-frontend/rule-builder-ui-spec.md`
- `docs/09-frontend/table-filter-sort-spec.md`
- `docs/09-frontend/fa-copy-dictionary.md`

## Allowed files/directories

- `frontend/app/`
- `frontend/components/`
- `frontend/lib/`
- `frontend/tests/`

## Forbidden changes

- Do not use SQLAdmin as HR workflow.
- Do not client-side filter full datasets.

## Implementation tasks

1. Build pages.
2. Build server-side table params.
3. Build Rule Builder UI.
4. Build application detail tabs.
5. Build AI analysis display.
6. Build notes/decision UI.

## Required tests/checks

- npm run lint
- frontend tests

## Acceptance criteria

- Pages match specs.
- Tables server-driven.
- AI separate from final decision view.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
