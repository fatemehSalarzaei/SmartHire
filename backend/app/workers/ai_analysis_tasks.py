from uuid import UUID

from app.db.session import SessionLocal
from app.services.ai_analysis_service import AIAnalysisService
from app.workers.celery_app import celery_app


@celery_app.task(name="ai.analyze_screening_application")
def analyze_screening_application(screening_application_id: str) -> dict[str, str | bool | None]:
    with SessionLocal() as db:
        try:
            outcome = AIAnalysisService(db).analyze_screening_application(
                UUID(screening_application_id),
            )
            db.commit()
            return {
                "used_output": outcome.used_output,
                "status": outcome.run.status.value,
                "error_code": outcome.error_code,
                "message_fa": outcome.message_fa,
            }
        except Exception:
            db.rollback()
            raise
