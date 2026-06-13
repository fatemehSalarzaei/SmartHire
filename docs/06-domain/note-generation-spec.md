# Note Generation Spec

Notes are internal SmartHire records.

## System note for not rejected

```text
بررسی خودکار توسط دستیار SmartHire انجام شد.
نتیجه: رزومه طبق قوانین فعلی رد نشد و نیازمند بررسی کارشناس جذب است.
اولویت بررسی: {priority_bucket}
امتیاز اولویت: {priority_score}/100
رتبه در این عنوان شغلی: {rank_in_job}
دلایل عبور: {decision_reasons}
دلایل امتیاز: {score_reasons}
نسخه قانون: {ruleset_name} v{ruleset_version}
```

## System note for rejected

```text
بررسی خودکار توسط دستیار SmartHire انجام شد.
نتیجه: رزومه در غربالگری داخلی رد شد.
دلایل رد: {decision_reasons}
نسخه قانون: {ruleset_name} v{ruleset_version}
```

## System note for needs review

```text
بررسی خودکار توسط دستیار SmartHire انجام شد.
نتیجه: تصمیم قطعی گرفته نشد و بررسی انسانی لازم است.
علت: {missing_fields_or_ambiguities}
امتیاز کمکی، در صورت امکان: {priority_score}/100
نسخه قانون: {ruleset_name} v{ruleset_version}
```

## Rules

- Generated system notes are not editable by HR.
- Recruiter notes are separate.
- Notes must not claim Kando status changed.
