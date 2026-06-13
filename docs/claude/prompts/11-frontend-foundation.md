# Task 11 — Frontend Foundation

## Goal

Implement Next.js foundation, auth flow, API client, layout, permissions and error handling.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/09-frontend/frontend-architecture.md`
- `docs/09-frontend/api-client-spec.md`
- `docs/09-frontend/frontend-error-handling.md`

## Allowed files/directories

- `frontend/`

## Forbidden changes

- Do not call Kando directly.
- Do not implement business decision logic in frontend.

## Implementation tasks

1. Create Next.js app structure.
2. Implement API client.
3. Implement auth state.
4. Implement layout.
5. Implement permission helpers.
6. Implement global error display.

## Required tests/checks

- npm run lint
- frontend unit tests

## Acceptance criteria

- API errors show Persian message.
- Auth flow works.
- No direct Kando calls.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
