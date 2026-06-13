from uuid import uuid4

import pytest
from sqlalchemy.sql.dml import Delete

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
    KandoJob,
    KandoRawPayload,
    KandoSyncState,
)
from app.services.kando_client import KandoPage
from app.services.kando_client import KandoClientError
from app.services.kando_sync_service import KandoSyncService


class _Result:
    def __init__(self, value=None) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, value: object) -> None:
        self.added.append(value)

    def flush(self) -> None:
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def execute(self, statement):
        if isinstance(statement, Delete):
            table_to_model = {
                "kando_cv_work_experiences": KandoCvWorkExperience,
                "kando_cv_university_degrees": KandoCvUniversityDegree,
                "kando_cv_language_skills": KandoCvLanguageSkill,
            }
            model_class = table_to_model[statement.table.name]
            kando_cv_id = _delete_kando_cv_id(statement)
            self.added = [
                item
                for item in self.added
                if not (
                    isinstance(item, model_class)
                    and getattr(item, "kando_cv_id", None) == kando_cv_id
                )
            ]
            return _Result(None)

        entity = statement.column_descriptions[0].get("entity")
        criteria = _criteria_values(statement)
        for item in reversed(self.added):
            if isinstance(item, entity) and all(getattr(item, key, None) == value for key, value in criteria.items()):
                return _Result(item)
        return _Result(None)


class FakeKandoClient:
    def __init__(self, pages: list[KandoPage]) -> None:
        self.pages = pages

    def iter_pages(self, fetch_page):
        return iter(self.pages)

    def get_jobs(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_applications(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_application_sources(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_candidates(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_cvs(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_cv_work_experiences(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_cv_university_degrees(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_cv_language_skills(self, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]

    def get_base_data(self, data_type: str, page_number: int = 1, page_size: int | None = None):
        return self.pages[page_number - 1]


def _page(endpoint_name: str, path: str, items: list[dict]) -> KandoPage:
    return KandoPage(
        endpoint_name=endpoint_name,
        path=path,
        page_number=1,
        page_size=100,
        items=items,
        raw_payload=items,
        total_count=len(items),
        status_code=200,
        duration_ms=12,
        retry_count=0,
    )


def _criteria_values(statement) -> dict[str, object]:
    values = {}
    for criterion in statement._where_criteria:
        values[criterion.left.name] = criterion.right.value
    return values


def _delete_kando_cv_id(statement) -> int:
    for criterion in statement._where_criteria:
        if criterion.left.name == "kando_cv_id":
            return criterion.right.value
    raise AssertionError("delete statement must filter by kando_cv_id")


def test_sync_service_persists_raw_payloads_logs_state_and_normalizes_jobs() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "jobs",
                    "/api/v1/Job/GetJobs",
                    [
                        {
                            "jobId": 2001,
                            "title": "کارشناس پشتیبانی و ارتباط با مشتری",
                        },
                    ],
                ),
            ],
        ),
    )

    processed = service.sync_jobs()

    assert processed == 1
    assert any(isinstance(item, KandoSyncState) and item.sync_name == "jobs" for item in db.added)
    assert any(isinstance(item, KandoRawPayload) and item.source == "jobs" for item in db.added)
    assert any(
        isinstance(item, KandoApiCallLog) and item.method == "GET" and item.endpoint == "/api/v1/Job/GetJobs"
        for item in db.added
    )
    jobs = [item for item in db.added if isinstance(item, KandoJob)]
    assert len(jobs) == 1
    assert jobs[0].kando_job_id == 2001
    assert jobs[0].title == "کارشناس پشتیبانی و ارتباط با مشتری"


def test_sync_service_normalizes_applications() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "applications",
                    "/api/v1/Application/GetApplications",
                    [
                        {
                            "applicationId": 1001,
                            "candidateId": 501,
                            "jobId": 2001,
                            "hireStepId": 3,
                            "statusId": 5,
                        },
                        {
                            "applicationId": 1002,
                            "candidateId": 502,
                            "jobId": 2001,
                            "hireStepId": 3,
                            "statusId": 5,
                        },
                        {
                            "applicationId": 1003,
                            "candidateId": 503,
                            "jobId": 2001,
                            "hireStepId": 3,
                            "statusId": 5,
                        },
                    ],
                ),
            ],
        ),
    )

    processed = service.sync_applications()

    assert processed == 3
    applications = [item for item in db.added if isinstance(item, KandoApplication)]
    assert [item.kando_application_id for item in applications] == [1001, 1002, 1003]
    assert applications[0].kando_candidate_id == 501
    assert applications[0].kando_job_id == 2001
    assert applications[0].kando_status_id == 5


def test_sync_service_normalizes_application_sources_with_source_id() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "application_sources",
                    "/api/v1/Application/GetApplicationSources",
                    [{"cvId": 123, "sourceId": 77, "sourceName": "LinkedIn"}],
                ),
            ],
        ),
    )

    processed = service.sync_application_sources()

    assert processed == 1
    raw_payloads = [item for item in db.added if isinstance(item, KandoRawPayload)]
    assert raw_payloads[0].external_id == 77
    assert raw_payloads[0].external_id != 123
    sources = [item for item in db.added if isinstance(item, KandoApplicationSource)]
    assert len(sources) == 1
    assert sources[0].kando_application_source_id == 77
    assert sources[0].name == "LinkedIn"


def test_sync_service_application_sources_do_not_fallback_to_cv_id() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "application_sources",
                    "/api/v1/Application/GetApplicationSources",
                    [{"cvId": 123, "sourceName": "Wrong"}],
                ),
            ],
        ),
    )

    with pytest.raises(KandoClientError) as exc_info:
        service.sync_application_sources()

    assert exc_info.value.code == ErrorCode.KANDO_UNEXPECTED_SCHEMA
    sources = [item for item in db.added if isinstance(item, KandoApplicationSource)]
    assert sources == []


def test_sync_service_normalizes_candidates() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "candidates",
                    "/api/v1/Candidate/GetCandidates",
                    [{"candidateId": 501, "firstName": "Sara", "lastName": "Ahmadi"}],
                ),
            ],
        ),
    )

    processed = service.sync_candidates()

    assert processed == 1
    candidates = [item for item in db.added if isinstance(item, KandoCandidate)]
    assert len(candidates) == 1
    assert candidates[0].kando_candidate_id == 501
    assert candidates[0].full_name == "Sara Ahmadi"


def test_sync_service_normalizes_cvs() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "cvs",
                    "/api/v1/Cv/GetCvs",
                    [{"cvId": 3001, "candidateId": 501}],
                ),
            ],
        ),
    )

    processed = service.sync_cvs()

    assert processed == 1
    cvs = [item for item in db.added if isinstance(item, KandoCv)]
    assert len(cvs) == 1
    assert cvs[0].kando_cv_id == 3001
    assert cvs[0].kando_candidate_id == 501


def test_sync_service_cv_work_experiences_are_idempotent_and_preserve_multiple_rows() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "cv_work_experiences",
                    "/api/v1/CV/GetCvWorkExperiences",
                    [
                        {"cvId": 3001, "roleTitle": "Support Specialist", "companyName": "A"},
                        {"cvId": 3001, "roleTitle": "Customer Success", "companyName": "B"},
                    ],
                ),
            ],
        ),
    )

    assert service.sync_cv_work_experiences() == 2
    assert service.sync_cv_work_experiences() == 2

    rows = [item for item in db.added if isinstance(item, KandoCvWorkExperience)]
    assert len(rows) == 2
    assert [row.title for row in rows] == ["Support Specialist", "Customer Success"]


def test_sync_service_cv_university_degrees_are_idempotent_and_preserve_multiple_rows() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "cv_university_degrees",
                    "/api/v1/Cv/GetCvUniversityDegrees",
                    [
                        {"cvId": 3001, "degreeName": "BSc", "universityName": "Tehran"},
                        {"cvId": 3001, "degreeName": "MSc", "universityName": "Sharif"},
                    ],
                ),
            ],
        ),
    )

    assert service.sync_cv_university_degrees() == 2
    assert service.sync_cv_university_degrees() == 2

    rows = [item for item in db.added if isinstance(item, KandoCvUniversityDegree)]
    assert len(rows) == 2
    assert [row.degree_name for row in rows] == ["BSc", "MSc"]


def test_sync_service_cv_language_skills_are_idempotent_and_preserve_multiple_rows() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "cv_language_skills",
                    "/api/v1/CV/GetCvLanguageSkills",
                    [
                        {"cvId": 3001, "languageId": 1, "skillLevelId": 3},
                        {"cvId": 3001, "languageId": 2, "skillLevelId": 2},
                    ],
                ),
            ],
        ),
    )

    assert service.sync_cv_language_skills() == 2
    assert service.sync_cv_language_skills() == 2

    rows = [item for item in db.added if isinstance(item, KandoCvLanguageSkill)]
    assert len(rows) == 2
    assert [(row.language_id, row.skill_level_id) for row in rows] == [(1, 3), (2, 2)]


def test_sync_service_normalizes_base_data() -> None:
    db = FakeDb()
    service = KandoSyncService(
        db,
        FakeKandoClient(
            [
                _page(
                    "base_data:industries",
                    "/api/v1/industries",
                    [{"id": 10, "titleFa": "نرم‌افزار", "titleEn": "Software"}],
                ),
            ],
        ),
    )

    processed = service.sync_base_data("industries")

    assert processed == 1
    cache_rows = [item for item in db.added if isinstance(item, KandoBaseDataCache)]
    assert len(cache_rows) == 1
    assert cache_rows[0].data_type == "industries"
    assert cache_rows[0].external_id == 10
    assert cache_rows[0].display_name == "نرم‌افزار"
