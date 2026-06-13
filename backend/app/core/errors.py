from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"


ERROR_MESSAGES_FA: dict[str, str] = {
    ErrorCode.VALIDATION_ERROR: "داده‌های ارسالی معتبر نیستند. لطفاً موارد مشخص‌شده را اصلاح کنید.",
    ErrorCode.UNAUTHENTICATED: "برای دسترسی به این بخش ابتدا وارد شوید.",
    ErrorCode.INVALID_CREDENTIALS: "ایمیل یا رمز عبور نادرست است.",
    ErrorCode.TOKEN_EXPIRED: "نشست شما منقضی شده است. لطفاً دوباره وارد شوید.",
    ErrorCode.PERMISSION_DENIED: "شما دسترسی لازم برای انجام این عملیات را ندارید.",
    ErrorCode.INTERNAL_ERROR: "خطای داخلی رخ داد. لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
    ErrorCode.NOT_FOUND: "منبع مورد نظر پیدا نشد.",
}


ERROR_RETRYABLE: dict[str, bool] = {
    ErrorCode.VALIDATION_ERROR: False,
    ErrorCode.UNAUTHENTICATED: False,
    ErrorCode.INVALID_CREDENTIALS: False,
    ErrorCode.TOKEN_EXPIRED: False,
    ErrorCode.PERMISSION_DENIED: False,
    ErrorCode.INTERNAL_ERROR: True,
    ErrorCode.NOT_FOUND: False,
}


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message_fa: str | None = None,
        status_code: int = 400,
        retryable: bool | None = None,
        field_errors: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message_fa = message_fa or ERROR_MESSAGES_FA.get(
            code,
            ERROR_MESSAGES_FA[ErrorCode.INTERNAL_ERROR],
        )
        self.status_code = status_code
        self.retryable = ERROR_RETRYABLE.get(code, False) if retryable is None else retryable
        self.field_errors = field_errors or {}
        super().__init__(self.code)


def message_fa_for_code(code: str) -> str:
    return ERROR_MESSAGES_FA.get(code, ERROR_MESSAGES_FA[ErrorCode.INTERNAL_ERROR])
