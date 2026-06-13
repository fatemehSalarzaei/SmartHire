---
name: smarthire-implementation
description: Use this skill when implementing a SmartHire task from docs/claude/prompts. It enforces source reading, file boundaries, tests, and completion reporting.
---

When implementing a SmartHire task:

1. Read `AGENTS.md`.
2. Read `CLAUDE.md`.
3. Read `docs/claude/context-index.md`.
4. Read `docs/claude/do-not-violate.md`.
5. Read the relevant task prompt from `docs/claude/prompts/`.
6. Extract allowed files and forbidden files.
7. Inspect existing implementation before editing.
8. Implement the smallest complete vertical slice.
9. Add or update tests and fixtures.
10. Run relevant checks.
11. Return the required completion report.

Never violate these project invariants:

- Kando is read-only.
- AI assists only; deterministic engines decide.
- Persian `message_fa` is required for backend API errors.
- Schema changes require Alembic migrations.
- Active RuleSets are versioned, not edited in place.
- No microservices, Kubernetes, Kafka, RabbitMQ, GraphQL, or extra infrastructure unless explicitly requested.
