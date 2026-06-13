from uuid import uuid4

from app.models.kando import (
    KandoApiCallLog,
    KandoApplication,
    KandoBaseDataCache,
    KandoJob,
    KandoRawPayload,
    KandoSyncState,
)
from app.services.kando_client import KandoPage
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
