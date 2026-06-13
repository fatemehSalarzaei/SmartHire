# Added Codex Files

The following files were added to make SmartHire easier and safer to implement with Codex:

- `AGENTS.md` — root implementation guidance for Codex.
- `backend/AGENTS.md` — backend-specific constraints and checks.
- `frontend/AGENTS.md` — frontend-specific constraints and checks.
- `infra/AGENTS.md` — deployment and infrastructure constraints.
- `docs/AGENTS.md` — documentation update rules.
- `.codex/config.toml` — project-level Codex guidance settings.
- `.codex/rules/default.rules` — approval gates for risky command classes.
- `.agents/skills/smarthire-implementation/SKILL.md` — reusable implementation workflow.
- `.agents/skills/smarthire-review/SKILL.md` — reusable review workflow.
- `docs/codex/task-runbook.md` — operational runbook for Codex task execution.
- `docs/codex/prompt-template.md` — prompt template for future Codex sessions.

A parent-level `SmartHire/AGENTS.md` was also added because the uploaded zip contains the actual implementation pack inside a nested directory. It tells Codex to work inside `smarthire_claude_implementation_pack 2/`.
