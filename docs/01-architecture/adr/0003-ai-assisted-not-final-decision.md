# ADR 0003 — AI Assists, Rule Engine Decides

## Decision

AI Analysis can summarize, extract semantic signals and propose reasons. It cannot be final decision-maker.

## Rationale

Hiring screening decisions must be deterministic, explainable and auditable.

## Consequences

- AI output must be JSON schema validated.
- AI errors must not stop the whole pipeline by default.
- HARD_REJECT based only on AI is disabled by default.
