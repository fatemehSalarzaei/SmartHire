from celery import Celery
from kombu import Queue

from app.core.config import settings

celery_app = Celery(
    "smarthire",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("sync"),
        Queue("ai_analysis"),
        Queue("screening"),
        Queue("ranking"),
    ),
    task_routes={
        "sync.kando_base_data": {"queue": "sync"},
        "sync.kando_jobs": {"queue": "sync"},
        "sync.kando_applications": {"queue": "sync"},
        "sync.build_application_snapshot": {"queue": "sync"},
        "ai.analyze_screening_application": {"queue": "ai_analysis"},
        "ai_analysis.run_for_application": {"queue": "ai_analysis"},
        "ai_analysis.run_for_job_batch": {"queue": "ai_analysis"},
        "ai_analysis.retry_failed": {"queue": "ai_analysis"},
        "screening.run_for_application": {"queue": "screening"},
        "screening.run_for_job": {"queue": "screening"},
        "screening.retry_failed": {"queue": "screening"},
        "ranking.calculate_for_job": {"queue": "ranking"},
        "ranking.calculate_for_application": {"queue": "ranking"},
        "ranking.recalculate_after_ruleset_change": {"queue": "ranking"},
        "maintenance.cleanup_old_raw_payloads": {"queue": "default"},
        "pipeline.run_for_application": {"queue": "default"},
    },
    beat_schedule={
        "sync-kando-base-data-daily": {
            "task": "sync.kando_base_data",
            "schedule": 24 * 60 * 60,
            "options": {"queue": "sync"},
        },
        "sync-kando-jobs-every-6-hours": {
            "task": "sync.kando_jobs",
            "schedule": 6 * 60 * 60,
            "options": {"queue": "sync"},
        },
        "sync-kando-applications-every-30-minutes": {
            "task": "sync.kando_applications",
            "schedule": 30 * 60,
            "options": {"queue": "sync"},
        },
        "retry-failed-ai-every-15-minutes": {
            "task": "ai_analysis.retry_failed",
            "schedule": 15 * 60,
            "options": {"queue": "ai_analysis"},
        },
        "cleanup-old-raw-payloads-nightly": {
            "task": "maintenance.cleanup_old_raw_payloads",
            "schedule": 24 * 60 * 60,
            "options": {"queue": "default"},
        },
    },
    task_track_started=True,
    worker_prefetch_multiplier=1,
    timezone=settings.app_timezone,
    enable_utc=True,
)

# Import task modules after celery_app exists so workers started from this
# module register every task.
from app.workers import ai_analysis_tasks as ai_analysis_tasks  # noqa: E402,F401
from app.workers import maintenance_tasks as maintenance_tasks  # noqa: E402,F401
from app.workers import pipeline_tasks as pipeline_tasks  # noqa: E402,F401
from app.workers import sync_tasks as sync_tasks  # noqa: E402,F401
