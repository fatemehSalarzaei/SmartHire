from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_generated_when_missing() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.headers["X-Request-ID"].startswith("req_")


def test_request_id_is_preserved_when_provided() -> None:
    client = TestClient(app)

    response = client.get("/healthz", headers={"X-Request-ID": "req_test"})

    assert response.headers["X-Request-ID"] == "req_test"

