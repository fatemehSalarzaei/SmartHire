from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.kando import KandoRawPayload
from app.services.worker_task_service import WorkerTaskLogService
from app.workers.celery_app import celery_app


@celery_app.task(name="maintenance.cleanup_old_raw_payloads", bind=True)
def cleanup_old_raw_payloads(self, retention_days: int = 30) -> dict[str, int]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    with SessionLocal() as db:
        logger = WorkerTaskLogService(db)
        log = logger.start(
            task_name="maintenance.cleanup_old_raw_payloads",
            task_id=getattr(getattr(self, "request", None), "id", None),
            queue_name="default",
            payload={"retention_days": retention_days},
        )
        try:
            result = db.execute(delete(KandoRawPayload).where(KandoRawPayload.received_at < cutoff))
            deleted = int(result.rowcount or 0)
            logger.complete(log, payload={"deleted": deleted})
            db.commit()
            return {"deleted": deleted}
        except Exception as exc:
            db.rollback()
            with SessionLocal() as error_db:
                error_logger = WorkerTaskLogService(error_db)
                error_log = error_logger.start(
                    task_name="maintenance.cleanup_old_raw_payloads",
                    task_id=getattr(getattr(self, "request", None), "id", None),
                    queue_name="default",
                    payload={"retention_days": retention_days},
                )
                error_logger.fail(
                    error_log,
                    error_code=exc.__class__.__name__.upper(),
                    message_fa="پاکسازی داده‌های خام قدیمی با خطا متوقف شد.",
                    retryable=True,
                )
                error_db.commit()
            raise
