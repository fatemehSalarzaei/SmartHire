# docs/AGENTS.md — SmartHire Documentation Rules

## Documentation role

Documents are contracts for implementation. Do not treat them as generic notes.

## Rules

- Keep docs concise, specific, and implementation-oriented.
- When code behavior changes, update the relevant contract document.
- Do not duplicate large sections across files.
- Prefer cross-references to duplication.
- Keep `docs/claude/context-index.md` and task prompts aligned with actual file names.
- If a task prompt references a missing file or wrong file name, fix the prompt or task index before implementation.

## Existing alignment requirement

`docs/claude/task-breakdown.md` must match the actual prompt filenames in `docs/claude/prompts/`.
