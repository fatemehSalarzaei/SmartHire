# Test Strategy

## Backend

- Unit tests: Rule Engine, Ranking Engine, Normalization, Note Generator.
- Integration tests: Kando client with mocked responses, API endpoints.
- Worker tests: idempotency, retry behavior, pipeline sequencing.
- Security tests: RBAC, masking, SQLAdmin access.

## Frontend

- Component tests: Rule Builder, tables, detail cards.
- API client tests: error handling and auth.
- E2E tests: login, applications list, application detail, note creation.

## Golden fixtures

Use `tests/fixtures/expected` to verify deterministic outcomes.
