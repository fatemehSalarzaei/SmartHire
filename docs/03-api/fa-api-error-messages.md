# Persian API Error Messages

All API errors must include a Persian user-facing message.

| Code | message_fa | Retryable |
|---|---|---|
| `KANDO_CONNECTION_FAILED` | اتصال به کندو برقرار نشد. لطفاً تنظیمات API و وضعیت دسترسی سرور را بررسی کنید. | true |
| `KANDO_AUTH_FAILED` | احراز هویت با کندو ناموفق بود. لطفاً کلید API و دسترسی IP را بررسی کنید. | false |
| `KANDO_RATE_LIMITED` | تعداد درخواست‌ها به کندو بیش از حد مجاز شده است. سامانه به‌صورت خودکار دوباره تلاش می‌کند. | true |
| `KANDO_SCHEMA_CHANGED` | ساختار پاسخ کندو با ساختار مورد انتظار سامانه سازگار نیست. | false |
| `RULESET_NOT_ACTIVE` | برای این عنوان شغلی قانون فعال تعریف نشده است. | false |
| `RULESET_ACTIVE_EDIT_FORBIDDEN` | قانون فعال قابل ویرایش مستقیم نیست. لطفاً نسخه جدید ایجاد کنید. | false |
| `APPLICATION_NOT_FOUND` | رزومه مورد نظر در سامانه پیدا نشد. | false |
| `SCREENING_ALREADY_UP_TO_DATE` | این رزومه با آخرین نسخه داده‌ها و قوانین قبلاً بررسی شده است. | false |
| `MANUAL_SCREENING_FORBIDDEN` | اجرای دستی غربالگری فقط برای ادمین فنی و بازپردازش مجاز است. | false |
| `AI_ANALYSIS_UNAVAILABLE` | تحلیل هوش مصنوعی در حال حاضر در دسترس نیست. رزومه با قوانین ساختاریافته بررسی شد. | true |
| `AI_SCHEMA_VALIDATION_FAILED` | خروجی هوش مصنوعی با ساختار مورد انتظار سامانه سازگار نبود و در تصمیم نهایی استفاده نشد. | false |
| `PERMISSION_DENIED` | شما دسترسی لازم برای انجام این عملیات را ندارید. | false |
| `VALIDATION_ERROR` | داده‌های ارسالی معتبر نیستند. لطفاً موارد مشخص‌شده را اصلاح کنید. | false |
| `INTERNAL_ERROR` | خطای داخلی رخ داد. لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید. | true |
