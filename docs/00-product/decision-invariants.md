# Decision Invariants

These are non-negotiable implementation rules.

## Product invariants

1. Kando is a read-only source in Phase 1.
2. SmartHire stores internal statuses, notes, decisions, scores and ranks.
3. No SmartHire worker, API or UI may change a Kando application status.
4. No SmartHire worker, API or UI may add a note to Kando.
5. Screening and ranking are automatic and worker-based.
6. Manual runs are only admin reprocess/debug/retry operations.
7. HR users review ready queues; they do not start daily screening manually.
8. Language uses skill level, not percentage.
9. Missing critical data defaults to `NEEDS_HUMAN_REVIEW`, not hard reject.
10. AI assists; Rule Engine and Ranking Engine decide.
11. AI output alone must never hard reject.
12. RuleSets are versioned; active RuleSets are not edited in place.
13. All API errors must include Persian `message_fa`.
14. All sensitive data must be protected by RBAC and masking.

## Engineering invariants

1. All schema changes require Alembic migration.
2. All new endpoints need schema validation and permission checks.
3. All background tasks must be idempotent.
4. Every external request must have timeout and retry policy.
5. Every decision must have audit trace.
6. Every production task must have tests or documented test gap.
