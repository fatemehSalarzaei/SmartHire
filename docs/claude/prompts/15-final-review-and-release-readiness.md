# Task 15 — Final Review and Release Readiness

## Goal

Run full project review against production quality gates and produce release readiness report.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/11-quality/production-quality-gates.md`
- `docs/12-deployment/release-checklist.md`
- `docs/claude/review-protocol.md`

## Allowed files/directories

- `docs/`
- `README.md`

## Forbidden changes

- Do not implement new features in final review unless fixing critical bug.

## Implementation tasks

1. Run full tests.
2. Check invariants.
3. Check no Kando write calls.
4. Check docs consistency.
5. Produce release readiness report.

## Required tests/checks

- make quality
- docker compose config
- grep for forbidden Kando write calls

## Acceptance criteria

- Quality gates passed or gaps explicitly listed.
- Release checklist updated.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
