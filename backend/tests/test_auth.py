from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.v1 import auth as auth_api
from app.core.auth import CurrentUser, require_permission
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db_session
from app.main import create_app
from app.models.audit import AuditLog


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []
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


class StubUser:
    def __init__(self) -> None:
        self.id = uuid4()
        self.email = "admin@example.com"
        self.full_name = "Admin User"
        self.is_active = True
        self.password_hash = "hidden"
        self.last_login_at = None


def _override_db(fake_db: FakeDb):
    def dependency():
        yield fake_db

    return dependency


def test_password_hash_verification_uses_hash_not_plaintext() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong", password_hash)


def test_login_success_returns_token_and_safe_user_data(monkeypatch) -> None:
    app = create_app()
    fake_db = FakeDb()
    user = StubUser()
    current_user = CurrentUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=frozenset({"SUPER_ADMIN"}),
        permissions=frozenset({"view_applications"}),
    )

    monkeypatch.setattr(auth_api, "authenticate_user", lambda db, email, password: user)
    monkeypatch.setattr(auth_api, "build_current_user", lambda db, user: current_user)
    app.dependency_overrides[get_db_session] = _override_db(fake_db)

    response = TestClient(app).post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "secret"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["access_token"]
    assert body["data"]["user"] == {
        "id": str(user.id),
        "email": "admin@example.com",
        "full_name": "Admin User",
        "roles": ["SUPER_ADMIN"],
        "permissions": ["view_applications"],
    }
    assert "password_hash" not in response.text
    assert fake_db.committed is True
    assert any(
        isinstance(record, AuditLog) and record.action == "LOGIN_SUCCESS"
        for record in fake_db.added
    )


def test_invalid_login_returns_401_with_persian_message(monkeypatch) -> None:
    app = create_app()
    fake_db = FakeDb()
    monkeypatch.setattr(auth_api, "authenticate_user", lambda db, email, password: None)
    app.dependency_overrides[get_db_session] = _override_db(fake_db)

    response = TestClient(app).post(
        "/api/v1/auth/login",
        json={"email": "bad@example.com", "password": "wrong"},
        headers={"X-Request-ID": "req_login"},
    )
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
    assert body["error"]["message_fa"] == "ایمیل یا رمز عبور نادرست است."
    assert body["error"]["request_id"] == "req_login"
    assert fake_db.committed is True
    assert any(
        isinstance(record, AuditLog) and record.action == "LOGIN_FAILURE"
        for record in fake_db.added
    )


def test_current_user_endpoint_requires_auth() -> None:
    response = TestClient(create_app()).get("/api/v1/me", headers={"X-Request-ID": "req_me"})
    body = response.json()

    assert response.status_code == 401
    assert body["error"]["code"] == "UNAUTHENTICATED"
    assert body["error"]["message_fa"] == "برای دسترسی به این بخش ابتدا وارد شوید."
    assert body["error"]["request_id"] == "req_me"


def test_invalid_token_returns_401_with_persian_message() -> None:
    response = TestClient(create_app()).get(
        "/api/v1/me",
        headers={"Authorization": "Bearer invalid.token.value", "X-Request-ID": "req_token"},
    )
    body = response.json()

    assert response.status_code == 401
    assert body["error"]["code"] == "UNAUTHENTICATED"
    assert body["error"]["message_fa"] == "برای دسترسی به این بخش ابتدا وارد شوید."
    assert body["error"]["request_id"] == "req_token"


def test_expired_token_returns_401_with_persian_message() -> None:
    token = create_access_token(
        subject=str(uuid4()),
        email="admin@example.com",
        expires_delta=timedelta(seconds=-1),
    )

    response = TestClient(create_app()).get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}", "X-Request-ID": "req_expired"},
    )
    body = response.json()

    assert response.status_code == 401
    assert body["error"]["code"] == "TOKEN_EXPIRED"
    assert body["error"]["message_fa"] == "نشست شما منقضی شده است. لطفاً دوباره وارد شوید."
    assert body["error"]["request_id"] == "req_expired"


def test_permission_denied_returns_persian_message_and_creates_audit() -> None:
    fake_db = FakeDb()
    current_user = CurrentUser(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        email="reviewer@example.com",
        full_name="Reviewer",
        roles=frozenset({"REVIEWER"}),
        permissions=frozenset({"view_applications"}),
    )

    from app.core.auth import get_current_user

    app = create_app()
    app.dependency_overrides[get_db_session] = _override_db(fake_db)
    app.dependency_overrides[get_current_user] = lambda: current_user

    @app.get("/needs-permission")
    def needs_permission_on_real_app(
        _current_user: CurrentUser = Depends(require_permission("admin_reprocess")),
    ) -> dict[str, bool]:
        return {"ok": True}

    response = TestClient(app).get("/needs-permission", headers={"X-Request-ID": "req_perm"})
    body = response.json()

    assert response.status_code == 403
    assert body["error"]["code"] == "PERMISSION_DENIED"
    assert body["error"]["message_fa"] == "شما دسترسی لازم برای انجام این عملیات را ندارید."
    assert body["error"]["request_id"] == "req_perm"
    assert fake_db.committed is True
    assert any(
        isinstance(record, AuditLog) and record.action == "PERMISSION_DENIED"
        for record in fake_db.added
    )
