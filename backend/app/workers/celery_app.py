from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "smarthire",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_default_queue="default",
    timezone=settings.app_timezone,
    enable_utc=True,
)

# Import task modules after celery_app exists so workers started from this module
# register the task names without relying on tests importing sync_tasks directly.
from app.workers import sync_tasks as sync_tasks  # noqa: E402,F401
from app.workers import ai_analysis_tasks as ai_analysis_tasks  # noqa: E402,F401
