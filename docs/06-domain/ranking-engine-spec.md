# Ranking Engine Spec

## Purpose

Ranking Engine scores and orders applications after Rule Engine decision.

## Inputs

- Application snapshot.
- Rule Engine decision.
- RuleSet scoring rules.
- Optional AI signals.

## Applicable statuses

Operational ranking applies to:

- `SMART_NOT_REJECTED`
- `NEEDS_HUMAN_REVIEW`

`SMART_REJECTED` may keep diagnostic score but does not enter recruiter priority queue.

## Score

Normalize to 0-100.

```text
normalized_score = clamp(base + bonuses - penalties, 0, max_score)
```

## Priority bucket

| Bucket | Default range |
|---|---|
| HIGH | score >= 75 |
| MEDIUM | 50 <= score < 75 |
| LOW | score < 50 |
| REVIEW_UNKNOWN | insufficient data |

## Rank

Rank per job by:

1. `priority_score` desc
2. passed gates desc
3. positive reasons count desc
4. missing fields count asc
5. application created/received date

## Output

- `screening_scores`
- `ranking_results`
- `screening_applications.priority_score`
- `screening_applications.priority_bucket`
- `screening_applications.rank_in_job`
