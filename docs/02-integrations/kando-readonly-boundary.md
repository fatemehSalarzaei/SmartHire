# Kando Read-only Boundary

## Allowed

- GET jobs.
- GET applications.
- GET candidates.
- GET CVs and structured CV components.
- GET BaseData.
- GET company read-only lookup data.
- GET application change states.

## Forbidden

- POST/PUT/PATCH/DELETE to Kando.
- Change application status.
- Reject application.
- Add Kando note.
- Add Kando tag.
- Move Kando hire step.
- Any browser/RPA automation to mutate Kando.

## Enforcement

- Kando client exposes only allowlisted GET methods.
- No generic `request(method, url, payload)` public API.
- Integration tests assert no non-GET Kando call exists.
- `docs/claude/do-not-violate.md` repeats this boundary.
