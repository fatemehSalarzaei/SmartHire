# Status Lifecycle

## Internal status flow

```text
NOT_REVIEWED
  -> NEEDS_HUMAN_REVIEW
  -> SMART_REJECTED
  -> SMART_NOT_REJECTED
  -> ERROR
  -> UNSUPPORTED_SOURCE
```

## Automatic flow

1. Application synced from Kando: `NOT_REVIEWED`.
2. Snapshot built and RuleSet found.
3. If insufficient data: `NEEDS_HUMAN_REVIEW`.
4. If hard reject gates match: `SMART_REJECTED`.
5. If pass/override conditions match: `SMART_NOT_REJECTED`.
6. If unsupported source or no CV data: `UNSUPPORTED_SOURCE`.
7. If processing failure: `ERROR` or `SYNC_ERROR`.

## Recruiter decision

Recruiter decision does not overwrite assistant decision. Store in separate `recruiter_decisions`.
