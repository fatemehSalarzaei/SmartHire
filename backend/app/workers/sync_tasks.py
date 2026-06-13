from app.db.session import SessionLocal
from sqlalchemy import select

from app.models.kando import KandoApplication
from app.services.kando_sync_service import KandoSyncService
from app.workers.celery_app import celery_app


@celery_app.task(name="sync.kando_applications")
def sync_kando_applications(enqueue_pipeline: bool = True) -> dict[str, int]:
    with SessionLocal() as db:
        try:
            service = KandoSyncService(db)
            result = {
                "applications": service.sync_applications(),
                "application_sources": service.sync_application_sources(),
                "candidates": service.sync_candidates(),
                "cvs": service.sync_cvs(),
                "cv_work_experiences": service.sync_cv_work_experiences(),
                "cv_university_degrees": service.sync_cv_university_degrees(),
                "cv_language_skills": service.sync_cv_language_skills(),
            }
            db.commit()
            if enqueue_pipeline:
                result["pipeline_enqueued"] = _enqueue_application_pipelines(db)
            return result
        except Exception:
            db.rollback()
            raise


@celery_app.task(name="sync.kando_jobs")
def sync_kando_jobs() -> dict[str, int]:
    with SessionLocal() as db:
        try:
            service = KandoSyncService(db)
            result = {
                "jobs": service.sync_jobs(),
                "hire_steps": service.sync_hire_steps(),
            }
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise


@celery_app.task(name="sync.kando_base_data")
def sync_kando_base_data() -> dict[str, int]:
    with SessionLocal() as db:
        try:
            result = KandoSyncService(db).sync_all_base_data()
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise


def _enqueue_application_pipelines(db) -> int:  # noqa: ANN001
    from app.workers.pipeline_tasks import run_full_pipeline_for_application

    application_ids = db.execute(
        select(KandoApplication.kando_application_id).order_by(
            KandoApplication.kando_application_id,
        ),
    ).scalars().all()
    for application_id in application_ids:
        run_full_pipeline_for_application.apply_async(
            args=[application_id],
            kwargs={"force": False, "run_ai": True},
            queue="default",
        )
    return len(application_ids)
