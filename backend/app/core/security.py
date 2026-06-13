import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from app.core.errors import AppError, ErrorCode

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _pbkdf2_digest(password=password, salt=salt, iterations=PBKDF2_ITERATIONS)
    return "$".join(
        [
            PBKDF2_ALGORITHM,
            str(PBKDF2_ITERATIONS),
            _b64encode(salt),
            _b64encode(digest),
        ],
    )


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False

    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        iterations = int(iterations_text)
        salt = _b64decode(salt_text)
        expected_digest = _b64decode(digest_text)
    except (ValueError, TypeError):
        return False

    if algorithm != PBKDF2_ALGORITHM or iterations <= 0:
        return False

    actual_digest = _pbkdf2_digest(password=password, salt=salt, iterations=iterations)
    return hmac.compare_digest(actual_digest, expected_digest)


def create_access_token(
    *,
    subject: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": subject,
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> dict[str, Any]:
    payload = _decode_jwt(token)
    if payload.get("type") != "access" or not payload.get("sub"):
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(datetime.now(timezone.utc).timestamp()):
        raise AppError(code=ErrorCode.TOKEN_EXPIRED, status_code=401)

    return payload


def _pbkdf2_digest(*, password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def _encode_jwt(payload: dict[str, Any]) -> str:
    if settings.jwt_algorithm != "HS256":
        raise AppError(code=ErrorCode.INTERNAL_ERROR, status_code=500)

    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64encode_json(header),
            _b64encode_json(payload),
        ],
    )
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def _decode_jwt(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)

    header_text, payload_text, signature_text = parts
    signing_input = f"{header_text}.{payload_text}"
    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    try:
        supplied_signature = _b64decode(signature_text)
        header = json.loads(_b64decode(header_text))
        payload = json.loads(_b64decode(payload_text))
    except (ValueError, TypeError):
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401) from None

    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)
    if header.get("alg") != settings.jwt_algorithm or header.get("typ") != "JWT":
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)
    if not isinstance(payload, dict):
        raise AppError(code=ErrorCode.UNAUTHENTICATED, status_code=401)

    return payload


def _b64encode_json(value: dict[str, Any]) -> str:
    serialized = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64encode(serialized)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))
