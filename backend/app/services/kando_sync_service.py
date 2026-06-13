import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import ErrorCode
from app.models.kando import (
    KandoApiCallLog,
    KandoApplication,
    KandoApplicationSource,
    KandoBaseDataCache,
    KandoCandidate,
    KandoCv,
    KandoCvLanguageSkill,
    KandoCvUniversityDegree,
    KandoCvWorkExperience,
    KandoHireStep,
    KandoJob,
    KandoRawPayload,
    KandoSyncState,
)
from app.services.kando_client import BASEDATA_ENDPOINTS, KandoClient, KandoClientError, KandoPage


class KandoSyncService:
    def __init__(self, db: Session, client: KandoClient | None = None) -> None:
        self.db = db
        self.client = client or KandoClient()
        self._replaced_work_experience_cv_ids: set[int] = set()
        self._replaced_university_degree_cv_ids: set[int] = set()
        self._replaced_language_skill_cv_ids: set[int] = set()

    def sync_jobs(self) -> int:
        return self._sync_paginated(
            sync_name="jobs",
            fetch_page=self.client.get_jobs,
            normalize_item=self._normalize_job,
        )

    def sync_hire_steps(self) -> int:
        return self._sync_paginated(
            sync_name="hire_steps",
            fetch_page=self.client.get_hire_steps,
            normalize_item=self._normalize_hire_step,
        )

    def sync_applications(self) -> int:
        return self._sync_paginated(
            sync_name="applications",
            fetch_page=self.client.get_applications,
            normalize_item=self._normalize_application,
        )

    def sync_application_sources(self) -> int:
        return self._sync_paginated(
            sync_name="application_sources",
            fetch_page=self.client.get_application_sources,
            normalize_item=self._normalize_application_source,
        )

    def sync_candidates(self) -> int:
        return self._sync_paginated(
            sync_name="candidates",
            fetch_page=self.client.get_candidates,
            normalize_item=self._normalize_candidate,
        )

    def sync_cvs(self) -> int:
        return self._sync_paginated(
            sync_name="cvs",
            fetch_page=self.client.get_cvs,
            normalize_item=self._normalize_cv,
        )

    def sync_cv_work_experiences(self) -> int:
        self._replaced_work_experience_cv_ids = set()
        return self._sync_paginated(
            sync_name="cv_work_experiences",
            fetch_page=self.client.get_cv_work_experiences,
            normalize_item=self._normalize_cv_work_experience,
        )

    def sync_cv_university_degrees(self) -> int:
        self._replaced_university_degree_cv_ids = set()
        return self._sync_paginated(
            sync_name="cv_university_degrees",
            fetch_page=self.client.get_cv_university_degrees,
            normalize_item=self._normalize_cv_university_degree,
        )

    def sync_cv_language_skills(self) -> int:
        self._replaced_language_skill_cv_ids = set()
        return self._sync_paginated(
            sync_name="cv_language_skills",
            fetch_page=self.client.get_cv_language_skills,
            normalize_item=self._normalize_cv_language_skill,
        )

    def sync_base_data(self, data_type: str) -> int:
        return self._sync_paginated(
            sync_name=f"base_data:{data_type}",
            fetch_page=lambda page_number, page_size: self.client.get_base_data(
                data_type,
                page_number,
                page_size,
            ),
            normalize_item=lambda item, raw_payload: self._normalize_base_data(
                data_type,
                item,
            ),
        )

    def sync_all_base_data(self) -> dict[str, int]:
        return {data_type: self.sync_base_data(data_type) for data_type in BASEDATA_ENDPOINTS}

    def _sync_paginated(
        self,
        *,
        sync_name: str,
        fetch_page: Callable[[int, int | None], KandoPage],
        normalize_item: Callable[[dict[str, Any], KandoRawPayload], None],
    ) -> int:
        now = datetime.now(timezone.utc)
        state = self._get_or_create_sync_state(sync_name)
        state.last_attempt_at = now
        processed = 0
        last_page = 0
        total_count: int | None = None
        try:
            for page in self.client.iter_pages(fetch_page):
                last_page = page.page_number
                total_count = page.total_count
                self._record_api_call(page)
                for item in page.items:
                    raw_payload = self._persist_raw_payload(
                        source=sync_name,
                        item=item,
                        external_id=_first_int(
                            item,
                            "id",
                            "jobId",
                            "applicationId",
                            "candidateId",
                            "cvId",
                            "hireStepId",
                            "sourceId",
                            "applicationSourceId",
                        ),
                    )
                    normalize_item(item, raw_payload)
                    processed += 1
            state.last_success_at = datetime.now(timezone.utc)
            state.cursor_json = {
                "last_page_synced": last_page,
                "total_count": total_count,
                "processed_count": processed,
                "last_error_code": None,
                "last_error_message_fa": None,
            }
        except KandoClientError as exc:
            state.cursor_json = {
                **(state.cursor_json or {}),
                "last_page_synced": last_page,
                "last_error_code": exc.code,
                "last_error_message_fa": exc.message_fa,
            }
            self.db.add(
                KandoApiCallLog(
                    method="GET",
                    endpoint=sync_name,
                    status_code=exc.status_code,
                    duration_ms=None,
                    retry_count=0,
                    error_code=exc.code,
                    message_fa=exc.message_fa,
                ),
            )
            raise
        return processed

    def _persist_raw_payload(
        self,
        *,
        source: str,
        item: dict[str, Any],
        external_id: int | None,
    ) -> KandoRawPayload:
        serialized = json.dumps(item, sort_keys=True, ensure_ascii=False).encode("utf-8")
        raw_payload = KandoRawPayload(
            source=source,
            external_id=external_id,
            payload_json=item,
            payload_hash=hashlib.sha256(serialized).hexdigest(),
            received_at=datetime.now(timezone.utc),
        )
        self.db.add(raw_payload)
        self.db.flush()
        return raw_payload

    def _record_api_call(self, page: KandoPage) -> None:
        self.db.add(
            KandoApiCallLog(
                method="GET",
                endpoint=page.path,
                status_code=page.status_code,
                duration_ms=page.duration_ms,
                retry_count=page.retry_count,
                error_code=None,
                message_fa=None,
            ),
        )

    def _get_or_create_sync_state(self, sync_name: str) -> KandoSyncState:
        state = self.db.execute(
            select(KandoSyncState).where(KandoSyncState.sync_name == sync_name),
        ).scalar_one_or_none()
        if state is None:
            state = KandoSyncState(sync_name=sync_name, cursor_json={})
            self.db.add(state)
            self.db.flush()
        return state

    def _normalize_job(self, item: dict[str, Any], raw_payload: KandoRawPayload) -> None:
        job_id = _required_int(item, "jobId")
        job = self._get_or_create(KandoJob, KandoJob.kando_job_id, job_id)
        job.kando_job_id = job_id
        job.title = _optional_str(item, "title")
        job.raw_payload_id = raw_payload.id

    def _normalize_hire_step(self, item: dict[str, Any], raw_payload: KandoRawPayload) -> None:
        step_id = _required_int(item, "hireStepId", "id")
        step = self._get_or_create(KandoHireStep, KandoHireStep.kando_hire_step_id, step_id)
        step.kando_hire_step_id = step_id
        step.kando_job_id = _first_int(item, "jobId")
        step.name = _optional_str(item, "name", "title")

    def _normalize_application(self, item: dict[str, Any], raw_payload: KandoRawPayload) -> None:
        application_id = _required_int(item, "applicationId")
        application = self._get_or_create(
            KandoApplication,
            KandoApplication.kando_application_id,
            application_id,
        )
        application.kando_application_id = application_id
        application.kando_candidate_id = _required_int(item, "candidateId")
        application.kando_cv_id = _first_int(item, "cvId")
        application.kando_job_id = _required_int(item, "jobId")
        application.kando_hire_step_id = _first_int(item, "hireStepId")
        application.kando_status_id = _first_int(item, "statusId")
        application.source_name = _optional_str(item, "sourceName", "jobBoardCompanyName")
        application.raw_payload_id = raw_payload.id
        application.last_synced_at = datetime.now(timezone.utc)

    def _normalize_application_source(
        self,
        item: dict[str, Any],
        raw_payload: KandoRawPayload,
    ) -> None:
        source_id = _first_int(item, "sourceId", "applicationSourceId", "id")
        if source_id is None:
            raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)
        source = self._get_or_create(
            KandoApplicationSource,
            KandoApplicationSource.kando_application_source_id,
            source_id,
        )
        source.kando_application_source_id = source_id
        source.name = _optional_str(item, "name", "sourceName", "jobBoardCompanyName") or "unknown"

    def _normalize_candidate(self, item: dict[str, Any], raw_payload: KandoRawPayload) -> None:
        candidate_id = _required_int(item, "candidateId")
        candidate = self._get_or_create(KandoCandidate, KandoCandidate.kando_candidate_id, candidate_id)
        candidate.kando_candidate_id = candidate_id
        candidate.full_name = _optional_str(item, "fullName", "name") or _join_name_parts(
            item,
            "firstName",
            "lastName",
        )
        candidate.raw_payload_id = raw_payload.id

    def _normalize_cv(self, item: dict[str, Any], raw_payload: KandoRawPayload) -> None:
        cv_id = _required_int(item, "cvId")
        cv = self._get_or_create(KandoCv, KandoCv.kando_cv_id, cv_id)
        cv.kando_cv_id = cv_id
        cv.kando_candidate_id = _first_int(item, "candidateId")
        cv.raw_payload_id = raw_payload.id

    def _normalize_cv_work_experience(
        self,
        item: dict[str, Any],
        raw_payload: KandoRawPayload,
    ) -> None:
        kando_cv_id = _required_int(item, "cvId")
        self._delete_cv_children_once(
            KandoCvWorkExperience,
            kando_cv_id,
            self._replaced_work_experience_cv_ids,
        )
        self.db.add(
            KandoCvWorkExperience(
                kando_cv_id=kando_cv_id,
                cv_id=self._cv_internal_id(item),
                title=_optional_str(item, "roleTitle", "title"),
                company_name=_optional_str(item, "companyName"),
                payload_json=item,
            ),
        )

    def _normalize_cv_university_degree(
        self,
        item: dict[str, Any],
        raw_payload: KandoRawPayload,
    ) -> None:
        kando_cv_id = _required_int(item, "cvId")
        self._delete_cv_children_once(
            KandoCvUniversityDegree,
            kando_cv_id,
            self._replaced_university_degree_cv_ids,
        )
        self.db.add(
            KandoCvUniversityDegree(
                kando_cv_id=kando_cv_id,
                cv_id=self._cv_internal_id(item),
                degree_name=_optional_str(item, "degreeName", "academicFieldName"),
                university_name=_optional_str(item, "universityName"),
                payload_json=item,
            ),
        )

    def _normalize_cv_language_skill(
        self,
        item: dict[str, Any],
        raw_payload: KandoRawPayload,
    ) -> None:
        kando_cv_id = _required_int(item, "cvId")
        self._delete_cv_children_once(
            KandoCvLanguageSkill,
            kando_cv_id,
            self._replaced_language_skill_cv_ids,
        )
        self.db.add(
            KandoCvLanguageSkill(
                kando_cv_id=kando_cv_id,
                cv_id=self._cv_internal_id(item),
                language_id=_first_int(item, "languageId"),
                skill_level_id=_first_int(item, "skillLevelId"),
                payload_json=item,
            ),
        )

    def _normalize_base_data(self, data_type: str, item: dict[str, Any]) -> None:
        external_id = _required_int(item, "id")
        cache = self.db.execute(
            select(KandoBaseDataCache).where(
                KandoBaseDataCache.data_type == data_type,
                KandoBaseDataCache.external_id == external_id,
            ),
        ).scalar_one_or_none()
        if cache is None:
            cache = KandoBaseDataCache(
                data_type=data_type,
                external_id=external_id,
                payload_json={},
            )
            self.db.add(cache)
        cache.display_name = _optional_str(item, "titleFa", "title", "name", "titleEn")
        cache.payload_json = item

    def _cv_internal_id(self, item: dict[str, Any]):
        cv_id = _required_int(item, "cvId")
        cv = self.db.execute(select(KandoCv).where(KandoCv.kando_cv_id == cv_id)).scalar_one_or_none()
        return cv.id if cv is not None else None

    def _delete_cv_children_once(self, model_class, kando_cv_id: int, replaced_cv_ids: set[int]) -> None:
        if kando_cv_id in replaced_cv_ids:
            return
        self.db.execute(delete(model_class).where(model_class.kando_cv_id == kando_cv_id))
        replaced_cv_ids.add(kando_cv_id)

    def _get_or_create(self, model_class, column, value):
        instance = self.db.execute(select(model_class).where(column == value)).scalar_one_or_none()
        if instance is None:
            instance = model_class()
            self.db.add(instance)
        return instance


def _required_int(item: dict[str, Any], *keys: str) -> int:
    value = _first_int(item, *keys)
    if value is None:
        raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)
    return value


def _first_int(item: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _optional_str(item: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str):
            return value
    return None


def _join_name_parts(item: dict[str, Any], *keys: str) -> str | None:
    parts = [_optional_str(item, key) for key in keys]
    full_name = " ".join(part for part in parts if part)
    return full_name or None
