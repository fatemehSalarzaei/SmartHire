# AI-Assisted Resume Analysis Spec

## Principle

AI assists. Rule Engine decides. Ranking Engine scores and orders.

AI Analysis is an independent pipeline step that produces validated JSON signals. It is not the source of final decision.

## Allowed uses

- Semantic related-experience detection.
- Persian resume summary.
- Positive/negative signal extraction.
- Ambiguity detection.
- Semantic/fuzzy matching support.
- Suggested score reasons.
- Persian explanation draft.

## Forbidden uses

- Hard reject solely by AI.
- Pass solely by AI.
- Mutating Kando or SmartHire state directly.
- Sending sensitive contact data to external AI.
- Inferring sensitive traits unrelated to the job.
- Treating hallucinated explanations as facts.

## Pipeline position

```text
Snapshot Builder -> AI Analysis -> Rule Engine -> Ranking Engine
```

## Failure behavior

If AI fails:

- Persist failed run with Persian error.
- Continue screening with structured data unless RuleSet explicitly requires AI.
- If RuleSet requires AI, send to `NEEDS_HUMAN_REVIEW`, not reject.
