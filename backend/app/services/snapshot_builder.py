import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.kando import (
    KandoApplication,
    KandoApplicationSource,
    KandoBaseDataCache,
    KandoCandidate,
    KandoCv,
    KandoCvLanguageSkill,
    KandoCvUniversityDegree,
    KandoCvWorkExperience,
    KandoJob,
)
from app.services.normalization_service import NormalizationService

SNAPSHOT_VERSION = "v1"
HASH_PREFIX = "sha256:"
CONTACT_KEYS = {"email", "mobile", "phone", "telephone", "address"}


@dataclass(frozen=True)
class SnapshotBuildResult:
    snapshot: dict[str, Any]
    snapshot_hash: str
    missing_fields: list[str]


class SnapshotBuilder:
    def __init__(
        self,
        db: Session,
        normalization_service: NormalizationService | None = None,
    ) -> None:
        self.db = db
        self.normalizer = normalization_service or NormalizationService()

    def build_for_kando_application_id(self, kando_application_id: int) -> SnapshotBuildResult:
        application = self._one_or_none(
            select(KandoApplication).where(KandoApplication.kando_application_id == kando_application_id),
        )
        if application is None:
            raise ValueError(f"Kando application not found: {kando_application_id}")

        job = self._one_or_none(select(KandoJob).where(KandoJob.kando_job_id == application.kando_job_id))
        candidate = self._one_or_none(
            select(KandoCandidate).where(KandoCandidate.kando_candidate_id == application.kando_candidate_id),
        )
        cv = None
        if application.kando_cv_id is not None:
            cv = self._one_or_none(select(KandoCv).where(KandoCv.kando_cv_id == application.kando_cv_id))

        work_experiences = self._all(
            select(KandoCvWorkExperience).where(KandoCvWorkExperience.kando_cv_id == application.kando_cv_id),
        )
        education = self._all(
            select(KandoCvUniversityDegree).where(KandoCvUniversityDegree.kando_cv_id == application.kando_cv_id),
        )
        language_skills = self._all(
            select(KandoCvLanguageSkill).where(KandoCvLanguageSkill.kando_cv_id == application.kando_cv_id),
        )
        application_sources = self._application_sources(application)

        missing_fields: set[str] = set()
        snapshot = {
            "snapshot_version": SNAPSHOT_VERSION,
            "snapshot_hash": None,
            "kando": self._kando_section(application, missing_fields),
            "job": self._job_section(job, missing_fields),
            "candidate": self._candidate_section(candidate, missing_fields),
            "cv": self._cv_section(cv, missing_fields),
            "application_sources": self._application_sources_section(application, application_sources),
            "work_experiences": self._work_experiences_section(work_experiences),
            "education": self._education_section(education),
            "language_skills": self._language_skills_section(language_skills),
            "software_skills": [],
            "missing_fields": [],
            "metadata": self._metadata_section(application),
        }

        self._add_collection_missing_fields(snapshot, missing_fields)
        snapshot["missing_fields"] = sorted(missing_fields)
        snapshot_hash = calculate_snapshot_hash(snapshot)
        snapshot["snapshot_hash"] = snapshot_hash
        return SnapshotBuildResult(
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            missing_fields=snapshot["missing_fields"],
        )

    def _kando_section(self, application: KandoApplication, missing_fields: set[str]) -> dict[str, Any]:
        if application.kando_cv_id is None:
            missing_fields.add("application.cv_id")
        return {
            "application_id": application.kando_application_id,
            "candidate_id": application.kando_candidate_id,
            "cv_id": application.kando_cv_id,
            "job_id": application.kando_job_id,
            "hire_step_id": application.kando_hire_step_id,
            "status_id": application.kando_status_id,
            "need_to_merge": _safe_payload_bool(application, "needToMerge"),
            "reject_time": _safe_payload_str(application, "rejectTime"),
        }

    def _job_section(self, job: KandoJob | None, missing_fields: set[str]) -> dict[str, Any]:
        title = self.normalizer.normalize_display_text(job.title if job is not None else None)
        if title is None:
            missing_fields.add("job.title")
        requirements = _safe_payload_str(job, "requirements", "requirement", "description")
        return {
            "title": title,
            "title_normalized": self.normalizer.normalize_for_matching(title),
            "requirements": self.normalizer.normalize_display_text(requirements),
        }

    def _candidate_section(
        self,
        candidate: KandoCandidate | None,
        missing_fields: set[str],
    ) -> dict[str, Any]:
        payload = _safe_payload(candidate)
        full_name = self.normalizer.normalize_display_text(candidate.full_name if candidate is not None else None)
        birth_date = _safe_payload_str(candidate, "birthDate", "birth_date")
        city = _safe_payload_str(candidate, "city", "cityName")
        if birth_date is None:
            missing_fields.add("candidate.birth_date")
        if city is None and payload.get("cityId") is None:
            missing_fields.add("candidate.city")
        return {
            "full_name": full_name,
            "full_name_normalized": self.normalizer.normalize_for_matching(full_name),
            "birth_date": birth_date,
            "age": _age_from_birth_date(birth_date),
            "city": self.normalizer.normalize_display_text(city),
        }

    def _cv_section(self, cv: KandoCv | None, missing_fields: set[str]) -> dict[str, Any]:
        about_me = _safe_payload_str(cv, "aboutMe", "about_me")
        skills = self.normalizer.normalize_string_list(_safe_payload(cv).get("skills"))
        if about_me is None:
            missing_fields.add("cv.about_me")
        if not skills:
            missing_fields.add("cv.skills")
        return {
            "about_me": self.normalizer.normalize_display_text(about_me),
            "about_me_normalized": self.normalizer.normalize_for_matching(about_me),
            "skills": skills,
            "skills_normalized": [self.normalizer.normalize_for_matching(skill) for skill in skills],
            "work_type": self.normalizer.normalize_display_text(_safe_payload_str(cv, "workType", "work_type")),
        }

    def _application_sources(self, application: KandoApplication) -> list[KandoApplicationSource]:
        if application.kando_cv_id is None:
            return []
        source_rows = self._all(
            select(KandoApplicationSource).where(KandoApplicationSource.kando_cv_id == application.kando_cv_id),
        )
        return sorted(
            source_rows,
            key=lambda row: (
                row.kando_application_source_id if row.kando_application_source_id is not None else 0,
                row.name,
            ),
        )

    def _application_sources_section(
        self,
        application: KandoApplication,
        sources: list[KandoApplicationSource],
    ) -> list[dict[str, Any]]:
        if sources:
            return [
                {
                    "source_name": self.normalizer.normalize_display_text(source.name),
                    "source_name_normalized": self.normalizer.normalize_for_matching(source.name),
                    "cv_id": source.kando_cv_id,
                    "cover_letter": self.normalizer.normalize_display_text(source.cover_letter),
                }
                for source in sources
            ]
        if application.source_name:
            return [
                {
                    "source_name": self.normalizer.normalize_display_text(application.source_name),
                    "source_name_normalized": self.normalizer.normalize_for_matching(application.source_name),
                    "cv_id": application.kando_cv_id,
                    "cover_letter": None,
                },
            ]
        return []

    def _work_experiences_section(self, rows: list[KandoCvWorkExperience]) -> list[dict[str, Any]]:
        items = [
            {
                "role_title": self.normalizer.normalize_display_text(row.title),
                "role_title_normalized": self.normalizer.normalize_for_matching(row.title),
                "company_name": self.normalizer.normalize_display_text(row.company_name),
                "company_name_normalized": self.normalizer.normalize_for_matching(row.company_name),
                "industry": self.normalizer.normalize_display_text(
                    _safe_payload_str(row, "industry", "industryName"),
                ),
                "description": self.normalizer.normalize_display_text(
                    _safe_payload_str(row, "achievementsDescription", "description"),
                ),
                "duration_months": _safe_payload_int(row, "durationMonths", "duration_months"),
            }
            for row in rows
        ]
        return sorted(
            items,
            key=lambda item: (
                item["role_title"] or "",
                item["company_name"] or "",
                item["duration_months"] or 0,
            ),
        )

    def _education_section(self, rows: list[KandoCvUniversityDegree]) -> list[dict[str, Any]]:
        items = [
            {
                "university_name": self.normalizer.normalize_display_text(row.university_name),
                "university_name_normalized": self.normalizer.normalize_for_matching(row.university_name),
                "field_name": self.normalizer.normalize_display_text(
                    row.degree_name or self._base_data_name("academic-fields", _safe_payload_int(row, "academicFieldId")),
                ),
                "degree_level": self.normalizer.normalize_display_text(
                    self._base_data_name("university-degree-levels", _safe_payload_int(row, "degreeLevelId")),
                ),
            }
            for row in rows
        ]
        return sorted(
            items,
            key=lambda item: (
                item["university_name"] or "",
                item["field_name"] or "",
                item["degree_level"] or "",
            ),
        )

    def _language_skills_section(self, rows: list[KandoCvLanguageSkill]) -> list[dict[str, Any]]:
        items = [
            {
                "language": self.normalizer.normalize_display_text(
                    self._base_data_name("languages", row.language_id),
                ),
                "language_normalized": self.normalizer.normalize_for_matching(
                    self._base_data_name("languages", row.language_id),
                ),
                "level": self.normalizer.normalize_display_text(
                    self._base_data_name("skill-levels", row.skill_level_id),
                ),
                "level_normalized": self.normalizer.normalize_for_matching(
                    self._base_data_name("skill-levels", row.skill_level_id),
                ),
                "language_id": row.language_id,
                "skill_level_id": row.skill_level_id,
            }
            for row in rows
        ]
        return sorted(
            items,
            key=lambda item: (
                item["language_id"] or 0,
                item["skill_level_id"] or 0,
                item["language"] or "",
            ),
        )

    def _metadata_section(self, application: KandoApplication) -> dict[str, Any]:
        built_at = None
        if application.last_synced_at is not None:
            built_at = _datetime_to_iso(application.last_synced_at)
        return {
            "original_resume_file_available": False,
            "built_at": built_at,
            "source": "normalized_kando_tables",
        }

    def _add_collection_missing_fields(self, snapshot: dict[str, Any], missing_fields: set[str]) -> None:
        if not snapshot["language_skills"]:
            missing_fields.add("language_skills")
        if not snapshot["work_experiences"]:
            missing_fields.add("work_experiences")

    def _base_data_name(self, data_type: str, external_id: int | None) -> str | None:
        if external_id is None:
            return None
        row = self._one_or_none(
            select(KandoBaseDataCache).where(
                KandoBaseDataCache.data_type == data_type,
                KandoBaseDataCache.external_id == external_id,
            ),
        )
        if row is None:
            return None
        return row.display_name or _safe_payload_str(row, "titleEn", "titleFa", "title", "name")

    def _one_or_none(self, statement):
        return self.db.execute(statement).scalar_one_or_none()

    def _all(self, statement) -> list:
        result = self.db.execute(statement)
        if hasattr(result, "scalars"):
            return list(result.scalars().all())
        value = result.scalar_one_or_none()
        return [] if value is None else [value]


def calculate_snapshot_hash(snapshot: dict[str, Any]) -> str:
    hash_input = {key: value for key, value in snapshot.items() if key != "snapshot_hash"}
    serialized = json.dumps(
        hash_input,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{HASH_PREFIX}{hashlib.sha256(serialized).hexdigest()}"


def _safe_payload(model: Any) -> dict[str, Any]:
    payload = getattr(model, "payload_json", None)
    if isinstance(payload, dict):
        return {key: value for key, value in payload.items() if key not in CONTACT_KEYS}
    return {}


def _safe_payload_str(model: Any, *keys: str) -> str | None:
    payload = _safe_payload(model)
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _safe_payload_int(model: Any, *keys: str) -> int | None:
    payload = _safe_payload(model)
    for key in keys:
        value = payload.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _safe_payload_bool(model: Any, *keys: str) -> bool | None:
    payload = _safe_payload(model)
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
    return None


def _age_from_birth_date(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    today = date.today()
    if parsed > today and parsed.year >= 1900:
        return None
    if 1200 <= parsed.year <= 1600:
        today_jalali = _gregorian_to_jalali(today)
        age = today_jalali[0] - parsed.year - (today_jalali[1:] < (parsed.month, parsed.day))
        return age if 0 <= age <= 120 else None
    if parsed.year < 1900:
        return None
    age = today.year - parsed.year - ((today.month, today.day) < (parsed.month, parsed.day))
    return age if age >= 0 else None


def _gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    gregorian_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    jalali_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy = value.year - 1600
    gm = value.month - 1
    gd = value.day - 1

    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    g_day_no += sum(gregorian_days_in_month[:gm]) + gd
    if gm > 1 and ((value.year % 4 == 0 and value.year % 100 != 0) or (value.year % 400 == 0)):
        g_day_no += 1

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    jm = 0
    while jm < 11 and j_day_no >= jalali_days_in_month[jm]:
        j_day_no -= jalali_days_in_month[jm]
        jm += 1

    return jy, jm + 1, j_day_no + 1


def _datetime_to_iso(value: datetime) -> str:
    if value.tzinfo is None:
        return value.isoformat()
    return value.isoformat().replace("+00:00", "Z")
