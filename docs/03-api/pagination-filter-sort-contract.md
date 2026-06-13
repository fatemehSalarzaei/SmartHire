# Pagination, Filter and Sort Contract

## Request

```http
GET /api/v1/applications?page=1&page_size=25&status=SMART_NOT_REJECTED&sort=-priority_score&q=ali
```

## Response

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 240,
    "total_pages": 10,
    "has_next": true,
    "has_previous": false
  }
}
```

## Sorting

- Prefix descending fields with `-`.
- Example: `sort=-priority_score,rank_in_job`.
- Sort whitelist is endpoint-specific.

## Filters

Filters must be explicit. Do not allow arbitrary SQL field names from the frontend.

Applications filters:

- `status`
- `priority_bucket`
- `job_id`
- `source`
- `english_level`
- `has_ai_signal`
- `created_from`
- `created_to`
- `screened_from`
- `screened_to`
