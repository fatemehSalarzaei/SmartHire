from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import IntegrationError, WorkerTaskLog

TASK_STATUS_STARTED = "STARTED"
TASK_STATUS_SUCCEEDED = "SUCCEEDED"
TASK_STATUS_FAILED = "FAILED"
TASK_STATUS_SKIPPED = "SKIPPED"
GENERIC_WORKER_ERROR_CODE = "WORKER_TASK_FAILED"
GENERIC_WORKER_ERROR_MESSAGE_FA = "اجرای وظیفه پس‌زمینه با خطا متوقف شد."


@dataclass(frozen=True)
class WorkerTaskLogOutcome:
    status: str
    task_name: str
    task_id: str | None
    queue_name: str | None
    error_code: str | None = None
    message_fa: str | None = None


class WorkerTaskLogService:
    """Small helper for append-style worker task logs and integration errors."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def start(
        self,
        *,
        task_name: str,
        task_id: str | None = None,
        queue_name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> WorkerTaskLog:
        log = WorkerTaskLog(
            task_name=task_name,
            task_id=task_id,
            queue_name=queue_name,
            status=TASK_STATUS_STARTED,
            started_at=datetime.now(timezone.utc),
            payload_json=_safe_payload(payload or {}),
        )
        self.db.add(log)
        self.db.flush()
        return log

    def complete(
        self,
        log: WorkerTaskLog,
        *,
        status: str = TASK_STATUS_SUCCEEDED,
        payload: dict[str, Any] | None = None,
    ) -> WorkerTaskLogOutcome:
        log.status = status
        log.completed_at = datetime.now(timezone.utc)
        if payload is not None:
            log.payload_json = {**(log.payload_json or {}), **_safe_payload(payload)}
        self.db.flush()
        return WorkerTaskLogOutcome(
            status=log.status,
            task_name=log.task_name,
            task_id=log.task_id,
            queue_name=log.queue_name,
        )

    def fail(
        self,
        log: WorkerTaskLog,
        *,
        error_code: str = GENERIC_WORKER_ERROR_CODE,
        message_fa: str = GENERIC_WORKER_ERROR_MESSAGE_FA,
        retryable: bool = True,
        payload: dict[str, Any] | None = None,
    ) -> WorkerTaskLogOutcome:
        log.status = TASK_STATUS_FAILED
        log.completed_at = datetime.now(timezone.utc)
        log.error_code = error_code
        log.message_fa = message_fa
        if payload is not None:
            log.payload_json = {**(log.payload_json or {}), **_safe_payload(payload)}
        self.db.add(
            IntegrationError(
                source="worker",
                error_code=error_code,
                message_fa=message_fa,
                retryable=retryable,
                context_json={
                    "task_name": log.task_name,
                    "task_id": log.task_id,
                    "queue_name": log.queue_name,
                    **_safe_payload(payload or {}),
                },
            ),
        )
        self.db.flush()
        return WorkerTaskLogOutcome(
            status=log.status,
            task_name=log.task_name,
            task_id=log.task_id,
            queue_name=log.queue_name,
            error_code=error_code,
            message_fa=message_fa,
        )


def _safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sensitive_tokens = ("password", "token", "authorization", "api_key", "secret")
    result: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(token in lowered for token in sensitive_tokens):
            result[str(key)] = "***MASKED***"
        elif isinstance(value, dict):
            result[str(key)] = _safe_payload(value)
        elif isinstance(value, list):
            result[str(key)] = [
                _safe_payload(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[str(key)] = value
    return result
