# Backend Testing Spec

## Required tests

- Kando client read-only allowlist.
- Pagination and retry behavior.
- Snapshot builder.
- Normalization.
- AI output schema validation.
- AI fallback behavior.
- Rule Engine decisions using fixtures.
- Ranking Engine using expected outputs.
- Persian error contract.
- RBAC permission checks.
- SQLAdmin access restrictions.
- Alembic migration import/check.

## Tools

- pytest
- pytest-asyncio
- httpx test client
- factory-boy or polyfactory
- respx for httpx mocks
