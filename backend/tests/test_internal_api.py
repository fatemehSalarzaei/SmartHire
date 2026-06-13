from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.schemas.common import PaginationMeta, PaginationParams, paginated_response


class FakeDb:
    def __init__(self) -> None:
        self.added = []
        self.committed = False
        self.rolled_back = False

    def add(self, value: object) -> None:
        self.added.append(value)

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def _override_db(fake_db: FakeDb):
    def dependency():
        yield fake_db

    return dependency


def _current_user_with_permissions(*permissions: str) -> CurrentUser:
    return CurrentUser(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        email="admin@example.com",
        full_name="Admin User",
        roles=frozenset({"SUPER_ADMIN"}),
        permissions=frozenset(permissions),
    )


def test_internal_api_routes_are_registered() -> None:
    app = create_app()
    paths = {getattr(route, "path", "") for route in app.routes}

    assert "/api/v1/jobs" in paths
    assert "/api/v1/rulesets" in paths
    assert "/api/v1/applications" in paths
    assert "/api/v1/screening/automation/status" in paths
    assert "/api/v1/screening/runs" in paths
    assert "/api/v1/admin/kando/test-connection" in paths


def test_paginated_response_shape_matches_contract() -> None:
    params = PaginationParams(page=2, page_size=25)
    response = paginated_response(
        data=[{"id": "1"}],
        meta=PaginationMeta.from_params(params, total=60),
    )

    assert response == {
        "success": True,
        "data": [{"id": "1"}],
        "pagination": {
            "page": 2,
            "page_size": 25,
            "total": 60,
            "total_pages": 3,
            "has_next": True,
            "has_previous": True,
        },
    }


def test_internal_api_protected_endpoint_requires_auth() -> None:
    response = TestClient(create_app()).get(
        "/api/v1/jobs",
        headers={"X-Request-ID": "req_internal_jobs"},
    )
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHENTICATED"
    assert body["error"]["message_fa"] == "برای دسترسی به این بخش ابتدا وارد شوید."
    assert body["error"]["request_id"] == "req_internal_jobs"


def test_internal_api_permission_denied_is_persian() -> None:
    app = create_app()
    fake_db = FakeDb()
    app.dependency_overrides[get_db_session] = _override_db(fake_db)
    app.dependency_overrides[get_current_user] = lambda: _current_user_with_permissions(
        "view_applications",
    )

    response = TestClient(app).post(
        f"/api/v1/screening/runs/{uuid4()}/retry",
        json={"force": False},
        headers={"X-Request-ID": "req_retry_denied"},
    )
    body = response.json()

    assert response.status_code == 403
    assert body["success"] is False
    assert body["error"]["code"] == "PERMISSION_DENIED"
    assert body["error"]["message_fa"] == "شما دسترسی لازم برای انجام این عملیات را ندارید."
    assert body["error"]["request_id"] == "req_retry_denied"
