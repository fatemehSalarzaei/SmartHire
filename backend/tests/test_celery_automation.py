from app.services.automation_service import PipelineStepResult, make_idempotency_key
from app.services.worker_task_service import WorkerTaskLogService
from app.workers.celery_app import celery_app


def test_task08_pipeline_tasks_are_registered_from_celery_app_startup() -> None:
    expected_tasks = {
        "sync.build_application_snapshot",
        "ai_analysis.run_for_application",
        "ai_analysis.run_for_job_batch",
        "ai_analysis.retry_failed",
        "screening.run_for_application",
        "screening.run_for_job",
        "screening.retry_failed",
        "ranking.calculate_for_application",
        "ranking.calculate_for_job",
        "ranking.recalculate_after_ruleset_change",
        "maintenance.cleanup_old_raw_payloads",
        "pipeline.run_for_application",
    }

    assert expected_tasks.issubset(set(celery_app.tasks))


def test_task08_queues_routes_and_beat_schedule_are_configured() -> None:
    queue_names = {queue.name for queue in celery_app.conf.task_queues}
    assert {"default", "sync", "ai_analysis", "screening", "ranking"}.issubset(queue_names)

    routes = celery_app.conf.task_routes
    assert routes["sync.build_application_snapshot"]["queue"] == "sync"
    assert routes["ai_analysis.run_for_application"]["queue"] == "ai_analysis"
    assert routes["screening.run_for_application"]["queue"] == "screening"
    assert routes["ranking.calculate_for_job"]["queue"] == "ranking"
    assert routes["maintenance.cleanup_old_raw_payloads"]["queue"] == "default"

    schedule = celery_app.conf.beat_schedule
    assert schedule["sync-kando-base-data-daily"]["task"] == "sync.kando_base_data"
    assert schedule["sync-kando-jobs-every-6-hours"]["task"] == "sync.kando_jobs"
    assert schedule["sync-kando-applications-every-30-minutes"]["task"] == "sync.kando_applications"
    assert schedule["retry-failed-ai-every-15-minutes"]["task"] == "ai_analysis.retry_failed"
    assert (
        schedule["cleanup-old-raw-payloads-nightly"]["task"]
        == "maintenance.cleanup_old_raw_payloads"
    )


def test_idempotency_key_is_stable_and_changes_with_inputs() -> None:
    first = make_idempotency_key("screening", 1001, "sha256:snapshot", "ruleset", 1)
    second = make_idempotency_key("screening", 1001, "sha256:snapshot", "ruleset", 1)
    changed = make_idempotency_key("screening", 1001, "sha256:changed", "ruleset", 1)

    assert first == second
    assert first.startswith("sha256:")
    assert first != changed


def test_pipeline_step_result_serializes_uuids_and_skip_status() -> None:
    result = PipelineStepResult(
        status="skipped",
        code="SNAPSHOT_UNCHANGED",
        message_fa="اسنپ‌شات رزومه نسبت به اجرای قبلی تغییری نداشته است.",
        kando_application_id=1001,
        kando_job_id=2001,
        snapshot_hash="sha256:abc",
        idempotency_key="sha256:key",
    )

    serialized = result.to_dict()

    assert result.skipped is True
    assert serialized["status"] == "skipped"
    assert serialized["code"] == "SNAPSHOT_UNCHANGED"
    assert serialized["message_fa"]
    assert serialized["snapshot_hash"] == "sha256:abc"


class FakeDb:
    def __init__(self) -> None:
        self.added = []
        self.flushed = 0

    def add(self, value) -> None:  # noqa: ANN001
        self.added.append(value)

    def flush(self) -> None:
        self.flushed += 1


def test_worker_task_log_service_masks_sensitive_payloads() -> None:
    db = FakeDb()
    service = WorkerTaskLogService(db)  # type: ignore[arg-type]

    log = service.start(
        task_name="pipeline.run_for_application",
        task_id="task-1",
        queue_name="default",
        payload={
            "kando_application_id": 1001,
            "api_key": "real-secret",
            "nested": {"authorization": "Bearer token"},
        },
    )

    assert log.payload_json["api_key"] == "***MASKED***"
    assert log.payload_json["nested"]["authorization"] == "***MASKED***"
    assert db.flushed == 1
