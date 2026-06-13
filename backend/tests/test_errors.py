from fastapi import Body
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import AppError, ErrorCode
from app.main import create_app


def _client_for_error_tests() -> TestClient:
    app = create_app()

    @app.get("/app-error")
    def app_error_route() -> None:
        raise AppError(
            code=ErrorCode.PERMISSION_DENIED,
            status_code=403,
        )

    @app.get("/unexpected-error")
    def unexpected_error_route() -> None:
        raise RuntimeError("internal stack detail")

    class Payload(BaseModel):
        count: int

    @app.post("/validate")
    def validation_route(payload: Payload = Body(...)) -> dict[str, int]:
        return {"count": payload.count}

    return TestClient(app, raise_server_exceptions=False)


def test_app_error_uses_persian_error_contract() -> None:
    client = _client_for_error_tests()

    response = client.get("/app-error", headers={"X-Request-ID": "req_app"})

    assert response.status_code == 403
    assert response.json() == {
        "success": False,
        "error": {
            "code": "PERMISSION_DENIED",
            "message_fa": "شما دسترسی لازم برای انجام این عملیات را ندارید.",
            "field_errors": {},
            "retryable": False,
            "request_id": "req_app",
        },
    }


def test_validation_error_uses_persian_error_contract() -> None:
    client = _client_for_error_tests()

    response = client.post("/validate", json={"count": "bad"}, headers={"X-Request-ID": "req_val"})
    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message_fa"] == (
        "داده‌های ارسالی معتبر نیستند. لطفاً موارد مشخص‌شده را اصلاح کنید."
    )
    assert body["error"]["field_errors"] == {"count": "این مقدار معتبر نیست."}
    assert body["error"]["retryable"] is False
    assert body["error"]["request_id"] == "req_val"


def test_unexpected_error_is_sanitized() -> None:
    client = _client_for_error_tests()

    response = client.get("/unexpected-error", headers={"X-Request-ID": "req_err"})
    body = response.json()

    assert response.status_code == 500
    assert body == {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message_fa": "خطای داخلی رخ داد. لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
            "field_errors": {},
            "retryable": True,
            "request_id": "req_err",
        },
    }
    assert "internal stack detail" not in response.text


def test_missing_route_uses_error_contract() -> None:
    client = TestClient(create_app(), raise_server_exceptions=False)

    response = client.get("/missing", headers={"X-Request-ID": "req_404"})
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message_fa"] == "منبع مورد نظر پیدا نشد."
    assert body["error"]["request_id"] == "req_404"
