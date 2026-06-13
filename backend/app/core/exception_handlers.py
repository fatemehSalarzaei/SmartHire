from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.errors import AppError, ErrorCode, message_fa_for_code
from app.core.middleware import REQUEST_ID_HEADER, get_request_id
from app.core.responses import error_response


def _json_error(
    *,
    request: Request,
    status_code: int,
    code: str,
    message_fa: str,
    retryable: bool,
    field_errors: dict[str, Any] | None = None,
) -> JSONResponse:
    request_id = get_request_id(request)
    response = JSONResponse(
        status_code=status_code,
        content=error_response(
            code=code,
            message_fa=message_fa,
            retryable=retryable,
            request_id=request_id,
            field_errors=field_errors,
        ),
    )
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return _json_error(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        message_fa=exc.message_fa,
        retryable=exc.retryable,
        field_errors=exc.field_errors,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = _code_for_http_status(exc.status_code)
    return _json_error(
        request=request,
        status_code=exc.status_code,
        code=code,
        message_fa=message_fa_for_code(code),
        retryable=code == ErrorCode.INTERNAL_ERROR,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _json_error(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=ErrorCode.VALIDATION_ERROR,
        message_fa=message_fa_for_code(ErrorCode.VALIDATION_ERROR),
        retryable=False,
        field_errors=_validation_field_errors(exc),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _json_error(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message_fa=message_fa_for_code(ErrorCode.INTERNAL_ERROR),
        retryable=True,
    )


def register_exception_handlers(app: Any) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


def _code_for_http_status(status_code: int) -> str:
    if status_code == status.HTTP_403_FORBIDDEN:
        return ErrorCode.PERMISSION_DENIED
    if status_code == status.HTTP_404_NOT_FOUND:
        return ErrorCode.NOT_FOUND
    if 400 <= status_code < 500:
        return ErrorCode.VALIDATION_ERROR
    return ErrorCode.INTERNAL_ERROR


def _validation_field_errors(exc: RequestValidationError) -> dict[str, str]:
    field_errors: dict[str, str] = {}
    for error in exc.errors():
        loc = error.get("loc", ())
        field = ".".join(str(part) for part in loc if part != "body") or "request"
        field_errors[field] = "این مقدار معتبر نیست."
    return field_errors
