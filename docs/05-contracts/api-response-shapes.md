# API Response Shapes

## Success single

```json
{
  "success": true,
  "data": {}
}
```

## Success list

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 100,
    "total_pages": 4,
    "has_next": true,
    "has_previous": false
  }
}
```

## Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message_fa": "داده‌های ارسالی معتبر نیستند. لطفاً موارد مشخص‌شده را اصلاح کنید.",
    "field_errors": {
      "name": ["نام الزامی است."]
    },
    "retryable": false,
    "request_id": "req_123"
  }
}
```

## Task accepted

```json
{
  "success": true,
  "data": {
    "task_id": "celery-task-id",
    "status": "PENDING",
    "message_fa": "درخواست بازپردازش ثبت شد."
  }
}
```
