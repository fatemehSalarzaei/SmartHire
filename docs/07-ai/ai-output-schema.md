# AI Output Schema

AI response must be JSON and validated by Pydantic.

## Example

```json
{
  "summary_fa": "کاندیدا سابقه پشتیبانی مشتری و مهارت زبان انگلیسی پیشرفته دارد.",
  "related_experience": {
    "is_related": true,
    "confidence": 0.82,
    "matched_categories": [
      "customer_support",
      "sales"
    ],
    "evidence": [
      "عنوان شغلی شامل Customer Support است"
    ]
  },
  "positive_signals": [
    {
      "code": "SUPPORT_EXPERIENCE",
      "label_fa": "سابقه پشتیبانی مشتری",
      "confidence": 0.86,
      "evidence": "Customer Support Specialist"
    }
  ],
  "negative_signals": [],
  "ambiguities": [
    {
      "code": "UNCLEAR_DURATION",
      "label_fa": "مدت سابقه کاری دقیق نیست",
      "severity": "LOW"
    }
  ],
  "suggested_score_reasons": [
    {
      "reason_code": "RELATED_SUPPORT_EXPERIENCE",
      "suggested_score_delta": 15,
      "explanation_fa": "سابقه مرتبط با پشتیبانی مشتری شناسایی شد"
    }
  ]
}
```

## Validation rules

- `summary_fa` required, Persian, concise.
- `confidence` values must be between 0 and 1.
- `evidence` must be grounded in provided input.
- Unknown signal codes are allowed only if tagged as `CUSTOM_*`.
- `suggested_score_delta` is advisory only; Ranking Engine decides.
- Invalid schema => `AI_SCHEMA_VALIDATION_FAILED`.
