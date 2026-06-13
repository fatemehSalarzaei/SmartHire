# Codex Prompt Template — SmartHire

Use this template when starting a Codex session for one implementation task.

```text
You are working inside the SmartHire repository.

First read:
- AGENTS.md
- CLAUDE.md
- docs/claude/context-index.md
- docs/claude/do-not-violate.md
- docs/claude/task-breakdown.md

Task:
Implement task <TASK_NUMBER> using:
- docs/claude/prompts/<PROMPT_FILE>.md

Rules:
- Follow AGENTS.md as the highest-priority project instruction.
- Respect all allowed/forbidden file boundaries in the task prompt.
- Keep the architecture monolith-first and worker-focused.
- Do not introduce microservices, Kubernetes, Kafka, RabbitMQ, GraphQL, CQRS, event sourcing, or service mesh.
- Do not write to Kando APIs.
- Add/update tests and fixtures relevant to the task.
- Run relevant checks.

Return:
STATUS: completed / partial / blocked
FILES_CHANGED:
- path
TESTS_RUN:
- command + result
RISKS:
- ...
NEXT_RECOMMENDED_TASK:
- ...
```
