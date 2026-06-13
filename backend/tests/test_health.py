from fastapi.testclient import TestClient

from app.main import app


def test_healthz_returns_standard_success_response() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"].startswith("req_")
    assert response.json() == {
        "success": True,
        "data": {"status": "ok", "service": "backend"},
    }


def test_api_healthz_alias_returns_standard_success_response() -> None:
    client = TestClient(app)

    response = client.get("/api/healthz")

    assert response.status_code == 200
    assert response.json()["success"] is True

