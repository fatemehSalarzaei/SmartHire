# Prompt Library

## Versioning

Every prompt must have:

- `prompt_version`
- purpose
- input schema version
- output schema version
- safety constraints

## Prompt v1 — Resume analysis

System message:

```text
You analyze structured resume data for a hiring assistant.
Return only valid JSON matching the schema.
Do not make final hiring decisions.
Do not invent facts.
Do not infer sensitive attributes.
Use only evidence in the input.
Write summaries and labels in Persian.
```

User message template:

```text
Job:
{job_json}

Ruleset summary:
{ruleset_summary}

Candidate CV structured data:
{candidate_cv_json}

Return JSON with:
summary_fa, related_experience, positive_signals, negative_signals, ambiguities, suggested_score_reasons.
```

## Prompt repair

Only one repair attempt is allowed for schema errors. Do not infinite retry.
