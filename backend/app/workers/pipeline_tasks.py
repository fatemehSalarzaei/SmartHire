from __future__ import annotations

from uuid import UUID

from app.db.session import SessionLocal
from app.services.automation_service import ScreeningAutomationService
from app.services.worker_task_service import WorkerTaskLogService
from app.workers.celery_app import celery_app

RETRY_KWARGS = {"max_retries": 3, "countdown": 60}


def _task_id(task_self) -> str | None:
    request = getattr(task_self, "request", None)
    value = getattr(request, "id", None)
    return str(value) if value else None


def _run_logged(task_self, *, task_name: str, queue_name: str, payload: dict, callback):
    with SessionLocal() as db:
        logger = WorkerTaskLogService(db)
        log = logger.start(
            task_name=task_name,
            task_id=_task_id(task_self),
            queue_name=queue_name,
            payload=payload,
        )
        try:
            result = callback(ScreeningAutomationService(db))
            if isinstance(result, list):
                serialized = [
                    item.to_dict() if hasattr(item, "to_dict") else item
                    for item in result
                ]
                failed = any(
                    isinstance(item, dict) and item.get("status") == "failed"
                    for item in serialized
                )
            else:
                serialized = result.to_dict() if hasattr(result, "to_dict") else result
                failed = isinstance(serialized, dict) and serialized.get("status") == "failed"
            logger.complete(
                log,
                status="FAILED" if failed else "SUCCEEDED",
                payload={"result": serialized},
            )
            db.commit()
            return serialized
        except Exception as exc:
            db.rollback()
            # Store the failure in a separate transaction so crashes are visible and retry-safe.
            with SessionLocal() as error_db:
                error_logger = WorkerTaskLogService(error_db)
                error_log = error_logger.start(
                    task_name=task_name,
                    task_id=_task_id(task_self),
                    queue_name=queue_name,
                    payload=payload,
                )
                error_logger.fail(
                    error_log,
                    error_code=exc.__class__.__name__.upper(),
                    message_fa="اجرای وظیفه پس‌زمینه با خطا متوقف شد.",
                    retryable=True,
                    payload={"error": str(exc)},
                )
                error_db.commit()
            raise task_self.retry(exc=exc, **RETRY_KWARGS) from exc


@celery_app.task(
    name="sync.build_application_snapshot",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def build_application_snapshot(self, kando_application_id: int, force: bool = False) -> dict:
    return _run_logged(
        self,
        task_name="sync.build_application_snapshot",
        queue_name="sync",
        payload={"kando_application_id": kando_application_id, "force": force},
        callback=lambda service: service.build_application_snapshot(
            kando_application_id,
            force=force,
        ),
    )


@celery_app.task(
    name="ai_analysis.run_for_application",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def run_ai_for_application(self, screening_application_id: str, force: bool = False) -> dict:
    return _run_logged(
        self,
        task_name="ai_analysis.run_for_application",
        queue_name="ai_analysis",
        payload={"screening_application_id": screening_application_id, "force": force},
        callback=lambda service: service.run_ai_for_application(
            UUID(screening_application_id),
            force=force,
        ),
    )


@celery_app.task(
    name="ai_analysis.run_for_job_batch",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def run_ai_for_job_batch(self, kando_job_id: int, force: bool = False) -> list[dict]:
    def callback(service: ScreeningAutomationService):
        build_results = service.build_snapshots_for_job(kando_job_id, force=False)
        ai_results = []
        for item in build_results:
            if item.screening_application_id is not None:
                ai_results.append(
                    service.run_ai_for_application(item.screening_application_id, force=force),
                )
        return ai_results

    return _run_logged(
        self,
        task_name="ai_analysis.run_for_job_batch",
        queue_name="ai_analysis",
        payload={"kando_job_id": kando_job_id, "force": force},
        callback=callback,
    )


@celery_app.task(name="ai_analysis.retry_failed", bind=True, autoretry_for=(), retry_backoff=True)
def retry_failed_ai(self, limit: int = 50) -> list[dict]:
    return _run_logged(
        self,
        task_name="ai_analysis.retry_failed",
        queue_name="ai_analysis",
        payload={"limit": limit},
        callback=lambda service: service.retry_failed_ai(limit=limit),
    )


@celery_app.task(
    name="screening.run_for_application",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def run_screening_for_application(self, screening_application_id: str, force: bool = False) -> dict:
    return _run_logged(
        self,
        task_name="screening.run_for_application",
        queue_name="screening",
        payload={"screening_application_id": screening_application_id, "force": force},
        callback=lambda service: service.run_screening_for_application(
            UUID(screening_application_id),
            force=force,
        ),
    )


@celery_app.task(name="screening.run_for_job", bind=True, autoretry_for=(), retry_backoff=True)
def run_screening_for_job(self, kando_job_id: int, force: bool = False) -> list[dict]:
    def callback(service: ScreeningAutomationService):
        build_results = service.build_snapshots_for_job(kando_job_id, force=False)
        screening_results = []
        for item in build_results:
            if item.screening_application_id is not None:
                screening_results.append(
                    service.run_screening_for_application(
                        item.screening_application_id,
                        force=force,
                    ),
                )
        return screening_results

    return _run_logged(
        self,
        task_name="screening.run_for_job",
        queue_name="screening",
        payload={"kando_job_id": kando_job_id, "force": force},
        callback=callback,
    )


@celery_app.task(name="screening.retry_failed", bind=True, autoretry_for=(), retry_backoff=True)
def retry_failed_screening(self, limit: int = 50) -> dict:
    # Screening validation/business failures are not blindly retried. Admin retry/reprocess can call
    # run_screening_for_application(..., force=True) explicitly.
    return _run_logged(
        self,
        task_name="screening.retry_failed",
        queue_name="screening",
        payload={"limit": limit},
        callback=lambda _service: {
            "status": "skipped",
            "code": "SCREENING_RETRY_REQUIRES_EXPLICIT_ADMIN_FORCE",
            "message_fa": "تکرار غربالگری فقط با درخواست صریح ادمین انجام می‌شود.",
        },
    )


@celery_app.task(
    name="ranking.calculate_for_application",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def calculate_ranking_for_application(
    self,
    screening_application_id: str,
    force: bool = False,
) -> dict:
    return _run_logged(
        self,
        task_name="ranking.calculate_for_application",
        queue_name="ranking",
        payload={"screening_application_id": screening_application_id, "force": force},
        callback=lambda service: service.calculate_ranking_for_application(
            UUID(screening_application_id),
            force=force,
        ),
    )


@celery_app.task(name="ranking.calculate_for_job", bind=True, autoretry_for=(), retry_backoff=True)
def calculate_ranking_for_job(self, kando_job_id: int, force: bool = False) -> list[dict]:
    return _run_logged(
        self,
        task_name="ranking.calculate_for_job",
        queue_name="ranking",
        payload={"kando_job_id": kando_job_id, "force": force},
        callback=lambda service: service.calculate_ranking_for_job(kando_job_id, force=force),
    )


@celery_app.task(
    name="ranking.recalculate_after_ruleset_change",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def recalculate_after_ruleset_change(self, kando_job_id: int) -> list[dict]:
    return _run_logged(
        self,
        task_name="ranking.recalculate_after_ruleset_change",
        queue_name="ranking",
        payload={"kando_job_id": kando_job_id},
        callback=lambda service: service.calculate_ranking_for_job(kando_job_id, force=True),
    )


@celery_app.task(
    name="pipeline.run_for_application",
    bind=True,
    autoretry_for=(),
    retry_backoff=True,
)
def run_full_pipeline_for_application(
    self,
    kando_application_id: int,
    force: bool = False,
    run_ai: bool = True,
) -> list[dict]:
    return _run_logged(
        self,
        task_name="pipeline.run_for_application",
        queue_name="default",
        payload={"kando_application_id": kando_application_id, "force": force, "run_ai": run_ai},
        callback=lambda service: service.run_full_pipeline_for_application(
            kando_application_id,
            force=force,
            run_ai=run_ai,
        ),
    )
