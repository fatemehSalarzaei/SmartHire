# ADR 0002 — Kando is Read-only in Phase 1

## Decision

Kando is treated as an external read-only source. SmartHire stores internal status, note, score and rank.

## Prohibited

- Kando status update.
- Kando note creation.
- Kando reject action.
- Kando stage movement.

## Rationale

Provided Kando documentation does not include confirmed write APIs for these operations.
