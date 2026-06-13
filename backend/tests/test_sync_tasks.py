from app.workers.celery_app import celery_app


def test_sync_tasks_are_registered_from_celery_app_startup() -> None:
    assert "sync.kando_applications" in celery_app.tasks
    assert "sync.kando_jobs" in celery_app.tasks
    assert "sync.kando_base_data" in celery_app.tasks
