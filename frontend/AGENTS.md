# frontend/AGENTS.md — SmartHire Frontend Rules

## Stack

Frontend uses:

- Next.js App Router
- TypeScript
- Tailwind CSS
- TanStack Query
- TanStack Table
- React Hook Form
- Zod
- shadcn/ui or MUI

## Required frontend documents

Before frontend work, read:

- `docs/09-frontend/frontend-architecture.md`
- `docs/09-frontend/frontend-folder-structure.md`
- `docs/09-frontend/api-client-spec.md`
- `docs/09-frontend/page-specs.md`
- `docs/09-frontend/ui-state-matrix.md`
- `docs/09-frontend/fa-copy-dictionary.md`
- `docs/09-frontend/table-filter-sort-spec.md`
- `docs/09-frontend/rule-builder-ui-spec.md`

## Frontend rules

- Frontend must not implement final screening/ranking decisions.
- Frontend consumes backend decision/ranking results.
- Tables must use server-side pagination, filtering, and sorting.
- Display Persian user-facing error messages from backend.
- Role-based UI hiding is presentation only; backend enforces permissions.
- Do not hardcode business rules in UI.
- Forms must validate with Zod or documented equivalent.
- Keep UX Persian-first where user-facing copy is required.

## Checks

When frontend changes, run the most relevant available checks:

```bash
npm run lint
npm test
npm run build
```

If Docker is required:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm test
docker compose exec frontend npm run build
```
