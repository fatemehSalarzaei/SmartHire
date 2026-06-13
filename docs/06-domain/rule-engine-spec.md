# Rule Engine Spec

## Purpose

The Rule Engine produces deterministic, auditable decisions for each application snapshot.

## Inputs

- Application snapshot.
- Active RuleSet version.
- Optional validated AI analysis result.

## Outputs

```json
{
  "decision": "SMART_NOT_REJECTED",
  "matched_rules": [],
  "missing_fields": [],
  "reasons": [],
  "confidence": 1.0
}
```

## Execution

1. Load active RuleSet for job.
2. Sort rule groups by priority.
3. Evaluate missing data policies.
4. Evaluate `NEEDS_REVIEW_GATE`.
5. Evaluate `REJECT_GATE`.
6. Evaluate `PASS_GATE`.
7. Evaluate `OVERRIDE_PASS`.
8. Produce decision and reason list.
9. Do not calculate rank here.

## RuleSet restrictions

- Rules are data, not code.
- Customer-support template is seed data, not hardcoded Python logic.
- Active RuleSet changes must create a new version.
- Rule explanations are required.
- Sensitive-field rules require elevated permission.

## AI target restrictions

AI targets can drive `SCORE_BONUS`, `SCORE_PENALTY`, or `NEEDS_REVIEW` by default. AI-driven `HARD_REJECT` is disabled unless explicitly enabled by `SUPER_ADMIN` and flagged in audit.
