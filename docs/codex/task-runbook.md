# SmartHire Codex Task Runbook

## Purpose

This runbook explains how Codex should execute SmartHire implementation tasks using the existing project documentation.

## Standard flow

1. Open the repository at `smarthire_claude_implementation_pack 2/`.
2. Read `AGENTS.md`.
3. Read `CLAUDE.md`.
4. Read `docs/claude/context-index.md`.
5. Read `docs/claude/do-not-violate.md`.
6. Choose the task prompt from `docs/claude/prompts/`.
7. Extract the allowed and forbidden file boundaries from the task prompt.
8. Inspect existing files before editing.
9. Implement the smallest complete vertical slice.
10. Add/update tests and fixtures.
11. Run relevant checks.
12. Return the completion report required by `AGENTS.md`.

## Task execution rules

- Do not skip task numbers unless the human explicitly changes the order.
- Do not silently expand scope.
- Do not introduce infrastructure that violates the small-system architecture guardrails.
- Do not treat AI output as a final hiring decision.
- Do not write to Kando APIs.
- Do not edit active RuleSets in place.
- Do not claim tests passed unless commands were run successfully.

## Review rule

For every completed task, produce a short implementation note under `docs/codex/` or the relevant docs directory when the task changes behavior, contracts, or operational assumptions.
