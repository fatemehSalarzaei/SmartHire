from app.workers.sync_tasks import sync_kando_applications, sync_kando_base_data, sync_kando_jobs


def test_sync_tasks_are_celery_wrappers() -> None:
    assert sync_kando_applications.name == "sync.kando_applications"
    assert sync_kando_jobs.name == "sync.kando_jobs"
    assert sync_kando_base_data.name == "sync.kando_base_data"
