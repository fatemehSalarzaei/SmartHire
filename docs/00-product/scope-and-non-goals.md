# Scope and Non-Goals

## Production-Ready Phase 1 scope

- Read-only integration with Kando ATS APIs.
- Automatic Kando sync.
- Automatic snapshot building.
- AI-assisted resume analysis.
- Rule Engine execution.
- Ranking Engine execution.
- Internal SmartHire status, note, score and rank storage.
- HR-facing Next.js panel.
- Technical SQLAdmin panel on `/admin`.
- RBAC, audit, Persian API error messages, observability and production quality gates.

## Explicit non-goals

- No Kando status update.
- No Kando note creation.
- No Kando stage movement.
- No Kando reject action.
- No PDF/Word resume parsing unless Kando later provides a file API.
- No language percentage logic.
- No LLM-only final decision.
- No HR manual daily screening execution.
- No use of SQLAdmin as HR workflow panel.

## Production-ready interpretation

Do not use Production-Ready Phase 1 shortcuts. If a feature is included in Phase 1, it must include validation, permissions, audit, tests and operational visibility.
