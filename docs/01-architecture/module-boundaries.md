# Module Boundaries

## Backend API

Owns:
- Auth and RBAC
- Internal API
- SQLAdmin mount
- Application query endpoints
- RuleSet management endpoints
- Recruiter note/decision endpoints

Must not:
- Put business decisions in routers.
- Call Kando directly from route handlers except test-connection endpoints through service layer.

## Kando Integration Service

Owns:
- Kando client
- Pagination, retry, timeout
- Raw response capture
- Normalized persistence
- Sync state

Must not:
- Mutate Kando.
- Interpret candidate suitability.

## Snapshot Builder

Owns:
- Canonical application snapshot
- Snapshot hash
- Missing-field detection

Must not:
- Make final decisions.

## AI Analysis Service

Owns:
- Prompt building
- LLM provider abstraction
- Output validation
- AI run/result persistence

Must not:
- Hard reject or pass candidates alone.

## Rule Engine

Owns:
- Deterministic decision.
- Matched rules.
- Missing-field policy.
- Reasons.

Must not:
- Call external APIs.

## Ranking Engine

Owns:
- Score, bucket, rank and tie breakers.

Must not:
- Change internal decision.

## Frontend

Owns:
- UI states.
- API consumption.
- HR workflow presentation.

Must not:
- Reimplement Rule Engine or Ranking Engine.
