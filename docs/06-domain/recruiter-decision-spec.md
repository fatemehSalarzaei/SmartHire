# Recruiter Decision Spec

Recruiter decision is separate from assistant decision.

## Values

- `RECRUITER_APPROVED_FOR_NEXT_STEP`
- `RECRUITER_REJECTED`
- `RECRUITER_NEEDS_MORE_INFO`
- `RECRUITER_CONTACT_CANDIDATE`

## Required fields

- application id
- decision
- optional note
- actor user
- created at

## Rules

- Recruiter decision does not mutate Kando.
- Recruiter decision does not overwrite `screening_decision`.
- Compare recruiter decision with assistant decision in reporting.
