# Task 07 — Rule Engine and Ranking Engine

## Goal

Implement deterministic Rule Engine and Ranking Engine using fixtures and expected outputs.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/06-domain/rule-engine-spec.md`
- `docs/06-domain/ranking-engine-spec.md`
- `docs/05-contracts/enums.md`
- `docs/11-quality/fixture-strategy.md`

## Allowed files/directories

- `backend/app/services/rule_engine.py`
- `backend/app/services/ranking_engine.py`
- `backend/tests/`
- `tests/fixtures/`

## Forbidden changes

- Do not hardcode customer-support rules in services.
- Do not use AI alone for hard reject.

## Implementation tasks

1. Implement rule operators.
2. Implement missing policy.
3. Implement AI target support with restrictions.
4. Implement score/bucket/rank.
5. Compare outputs to expected fixtures.

## Required tests/checks

- pytest rule/ranking golden tests

## Acceptance criteria

- Expected decisions match fixtures.
- Expected rankings match fixtures.
- AI-only hard reject prevented.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
