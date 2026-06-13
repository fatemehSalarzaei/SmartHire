from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SENSITIVE_KEY_FRAGMENTS = (
    "api_key",
    "apikey",
    "authorization",
    "token",
    "secret",
    "password",
    "password_hash",
    "encrypted_api_key",
    "mobile",
    "phone",
    "email",
    "address",
)

MASK = "***MASKED***"


def is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS)


def mask_secret(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return ""
    if len(text) <= 8:
        return MASK
    return f"{text[:4]}…{text[-4:]}"


def mask_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: MASK if is_sensitive_key(str(key)) else mask_json(item)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [mask_json(item) for item in value]
    return value


def format_masked_secret(model: Any, attribute: str) -> str | None:
    return mask_secret(getattr(model, attribute, None))


def format_masked_json(model: Any, attribute: str) -> Any:
    return mask_json(getattr(model, attribute, None))
