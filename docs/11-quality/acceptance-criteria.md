# Production Phase 1 Acceptance Criteria

1. Kando read-only sync works with pagination/retry.
2. No Kando write operation exists in code.
3. BaseData sync maps languages and skill levels.
4. Snapshot builder produces deterministic hash.
5. AI analysis runs independently and validates JSON.
6. AI failure does not block screening unless configured.
7. Rule Engine produces auditable decisions.
8. Ranking Engine produces score/bucket/rank.
9. Internal notes are generated in Persian.
10. Recruiter queues show ready ranked outputs.
11. SQLAdmin is restricted and read-only where required.
12. All API errors include `message_fa`.
13. Active RuleSet cannot be edited in place.
14. Alembic migrations exist for all models.
15. Fixture-based tests pass for decisions and rankings.
16. RBAC tests pass.
17. Sensitive data masking tests pass.
18. Celery tasks are idempotent.
19. Observability logs include request/task IDs.
20. Docker Compose local environment starts successfully.
