from typing import Any


def success_response(data: Any = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"success": True, "data": data}
    if meta is not None:
        response["meta"] = meta
    return response


def error_response(
    *,
    code: str,
    message_fa: str,
    retryable: bool,
    request_id: str,
    field_errors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message_fa": message_fa,
            "field_errors": field_errors or {},
            "retryable": retryable,
            "request_id": request_id,
        },
    }

