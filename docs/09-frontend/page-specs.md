# Page Specs

## `/login`

- Login form.
- Persian validation.
- Redirect by role.

## `/dashboard`

- Sync health.
- Screening/ranking run status.
- Counts by status.
- High priority queue count.
- Error count.

## `/jobs`

- Job table.
- Active RuleSet.
- Last synced.
- Applications count.
- Screening enabled flag.

## `/jobs/[jobId]/rulesets`

- RuleSet list.
- Create/clone RuleSet.
- Activate RuleSet with confirmation.
- Show version and status.

## `/jobs/[jobId]/rulesets/[rulesetId]`

- Rule Builder.
- Rule groups.
- Rules.
- Score/missing policy.
- Preview and validation.
- Active RuleSet cannot be edited in place.

## `/applications`

- Main recruiter queue.
- Status filters.
- Priority filters.
- AI signal badges.
- Score/rank sort.

## `/applications/[applicationId]`

Tabs/cards:
- Profile summary.
- Kando structured data.
- Screening decision.
- Score breakdown.
- AI analysis.
- Notes.
- Recruiter decision.

## `/screening-runs`

- Run list.
- Status.
- Counts.
- Errors.
- Admin-only retry.

## `/settings`

- Kando status read-only for HR.
- Admin settings link if permitted.
