---
name: smarthire-review
description: Use this skill when reviewing SmartHire implementation work for correctness, missing tests, architectural violations, and task compliance.
---

Review SmartHire work against:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/claude/do-not-violate.md`
4. Relevant task prompt under `docs/claude/prompts/`
5. Relevant architecture/domain/API/database/frontend/backend/security docs
6. Existing tests and fixtures

Check for:

- Kando write violations.
- AI final-decision violations.
- Missing Persian `message_fa`.
- Missing Alembic migration after model changes.
- Hardcoded business rules.
- Missing RuleSet versioning.
- Sensitive data exposure.
- Over-engineering against small-system constraints.
- Missing tests or unproven completion claims.
- Changed files outside allowed task scope.

Return review as:

```text
READY_TO_ACCEPT: yes/no
BLOCKERS:
- ...
ISSUES:
- ...
TEST_EVIDENCE:
- ...
REQUIRED_FIXES:
- ...
```
