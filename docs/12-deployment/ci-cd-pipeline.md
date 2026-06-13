# CI/CD Pipeline

## Pull request checks

- backend lint
- backend tests
- frontend lint
- frontend tests
- type checks
- migration check
- secret scan
- no Kando write endpoint grep/check
- fixture golden output tests

## Deploy stages

1. Build images.
2. Run tests.
3. Push images.
4. Deploy staging.
5. Smoke test.
6. Manual approval.
7. Deploy production.
8. Run health checks.
