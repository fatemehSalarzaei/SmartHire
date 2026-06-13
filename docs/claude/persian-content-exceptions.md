# Persian Content Exceptions

This implementation pack is English by default.

The following Persian content is intentionally retained because it is required for product behavior, vendor-source fidelity, test coverage, or Persian user-facing output.

## Required Persian user-facing output

- `docs/03-api/fa-api-error-messages.md`
- `docs/03-api/error-contract.md`
- `docs/05-contracts/api-response-shapes.md`
- `docs/06-domain/note-generation-spec.md`
- `docs/07-ai/ai-output-schema.md`
- `docs/07-ai/ai-fallback-policy.md`
- `docs/09-frontend/api-client-spec.md`
- `docs/09-frontend/fa-copy-dictionary.md`

Reason: API errors, UI copy, generated notes, and AI summaries must support Persian user-facing text.

## Required Persian normalization and matching examples

- `docs/05-contracts/snapshot-contract.md`
- `docs/06-domain/normalization-spec.md`

Reason: the system must normalize and match Persian names, universities, fields, roles, and Kando-originated text.

## Required Persian fixtures

- `tests/fixtures/**`

Reason: fixture data intentionally includes Persian job titles, candidate data, Kando lookup titles, expected Persian notes, expected Persian API errors, and AI output examples. These fixtures are required for production-grade tests.

## Vendor source files

- `docs/source/kando/**`

Reason: these are original Kando/Postman/PDF source artifacts. They must remain unchanged so Claude and developers can verify integration behavior against the original vendor material.

## Source reference examples

- `docs/source/smarthire_kando_screening_project_definition_v1_4_ai.md`
- `docs/source/smarthire_technology_stack_and_architecture_v1_3_ai.md`

Reason: these files are now English, but may contain required Persian examples inside JSON fields such as `message_fa`, `summary_fa`, `label_fa`, and `explanation_fa`.
