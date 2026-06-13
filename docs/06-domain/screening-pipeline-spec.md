# Screening Pipeline Spec

## Automatic production flow

```text
sync_kando_applications
  -> build_application_snapshot
  -> run_ai_analysis_if_enabled
  -> run_rule_engine
  -> run_ranking_engine
  -> generate_internal_note
  -> update_ready_queues
```

## Pipeline rules

- Must be idempotent.
- Must skip unchanged snapshots/rulesets unless force rerun.
- Must continue without AI if AI fails and RuleSet does not require AI.
- Must never call Kando write APIs.
- Must record `screening_run` and `screening_run_item`.
- Must record Persian error if failed.
- Must preserve all matched rules and missing fields.

## Decision precedence

1. Unsupported source / missing core CV data.
2. Kando already rejected policy.
3. Missing critical data policy.
4. Hard reject gates.
5. Pass gates and overrides.
6. Needs review gates.
7. Score and ranking.
8. Note generation.
