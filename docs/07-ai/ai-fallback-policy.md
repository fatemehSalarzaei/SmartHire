# AI Fallback Policy

## AI unavailable

Result:

```json
{
  "error_code": "AI_ANALYSIS_UNAVAILABLE",
  "message_fa": "تحلیل هوش مصنوعی در حال حاضر در دسترس نیست. رزومه با قوانین ساختاریافته بررسی شد.",
  "retryable": true
}
```

Action:

- Continue Rule Engine if AI not mandatory.
- Mark AI run failed.
- Retry with backoff.

## AI schema invalid

Result:

```json
{
  "error_code": "AI_SCHEMA_VALIDATION_FAILED",
  "message_fa": "خروجی هوش مصنوعی با ساختار مورد انتظار سامانه سازگار نبود و در تصمیم نهایی استفاده نشد.",
  "retryable": false
}
```

Action:

- Do not use AI output.
- Continue structured-data screening.

## AI required by RuleSet

If RuleSet marks AI as required and AI fails:

- Decision: `NEEDS_HUMAN_REVIEW`.
- Never hard reject.
