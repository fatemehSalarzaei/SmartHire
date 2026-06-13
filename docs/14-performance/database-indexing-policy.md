# Database Indexing Policy

Add indexes for:

- application job/status/bucket queries.
- rank and score sorting.
- created/synced/screened dates.
- ruleset active lookup.
- AI run status lookup.
- audit created date.

Avoid premature GIN indexes on JSONB until query pattern is confirmed.
