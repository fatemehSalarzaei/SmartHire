# Snapshot Contract

Rule Engine, Ranking Engine and AI Analysis must use the canonical application snapshot, not scattered database models.

## Snapshot lifecycle

```text
Kando raw payloads -> normalized tables -> snapshot -> snapshot_hash -> AI/Rule/Ranking
```

## Required properties

- Deterministic.
- Hashable.
- Versioned.
- Contains only needed structured data.
- Marks missing fields explicitly.
- Does not include Kando API key.
- Does not include full raw payload.
- Does not include contact data in AI input by default.

## Example

```json
{
  "snapshot_version": "v1",
  "snapshot_hash": "sha256:...",
  "kando": {
    "application_id": 1001,
    "candidate_id": 501,
    "cv_id": 9001,
    "job_id": 2001,
    "hire_step_id": 3,
    "status_id": 5,
    "need_to_merge": false,
    "reject_time": null
  },
  "job": {
    "title": "کارشناس پشتیبانی و ارتباط با مشتری",
    "requirements": "..."
  },
  "candidate": {
    "full_name": "نمونه کارجو",
    "birth_date": "1374-01-01",
    "age": 31,
    "city": "تهران"
  },
  "cv": {
    "about_me": "...",
    "skills": [
      "CRM",
      "English"
    ],
    "work_type": null
  },
  "application_sources": [
    {
      "source_name": "جاب‌ویژن",
      "cv_id": 9001,
      "cover_letter": "..."
    }
  ],
  "work_experiences": [
    {
      "role_title": "Customer Support Specialist",
      "company_name": "Example",
      "industry": "SaaS",
      "description": "...",
      "duration_months": 24
    }
  ],
  "education": [
    {
      "university_name": "دانشگاه تهران",
      "field_name": "زبان انگلیسی",
      "degree_level": "Bachelor"
    }
  ],
  "language_skills": [
    {
      "language": "English",
      "level": "Advanced"
    }
  ],
  "software_skills": [],
  "missing_fields": [],
  "metadata": {
    "original_resume_file_available": false,
    "built_at": "2026-06-10T00:00:00Z"
  }
}
```
