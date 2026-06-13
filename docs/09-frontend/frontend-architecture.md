# Frontend Architecture

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui or MUI
- TanStack Query
- TanStack Table
- React Hook Form
- Zod

## Principles

- Frontend does not implement business decisions.
- Frontend consumes backend decision/ranking data.
- All tables use server-side pagination/filter/sort.
- All errors display Persian messages from backend.
- Role-based UI hiding is presentation only; backend enforces permissions.
