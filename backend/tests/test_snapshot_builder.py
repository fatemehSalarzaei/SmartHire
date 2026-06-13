import json
from datetime import datetime, timezone
from uuid import uuid4

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
from app.services.snapshot_builder import SnapshotBuilder


class _ScalarResult:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class _Result:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def scalar_one_or_none(self):
        return self.values[0] if self.values else None

    def scalars(self) -> _ScalarResult:
        return _ScalarResult(self.values)


class FakeDb:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def execute(self, statement):
        entity = statement.column_descriptions[0].get("entity")
        criteria = _criteria_values(statement)
        matches = [
            row
            for row in self.rows
            if isinstance(row, entity)
            and all(getattr(row, key, None) == value for key, value in criteria.items())
        ]
        return _Result(matches)


def _criteria_values(statement) -> dict[str, object]:
    values = {}
    for criterion in statement._where_criteria:
        try:
            value = criterion.right.value
        except AttributeError:
            value = None
        values[criterion.left.name] = value
    return values


def _make_row(model_class, **values):
    row = model_class()
    row.id = uuid4()
    for key, value in values.items():
        setattr(row, key, value)
    return row


def _base_rows() -> list[object]:
    synced_at = datetime(2026, 6, 10, tzinfo=timezone.utc)
    return [
        _make_row(
            KandoApplication,
            kando_application_id=1001,
            kando_candidate_id=501,
            kando_cv_id=9001,
            kando_job_id=2001,
            kando_hire_step_id=3,
            kando_status_id=5,
            source_name="جاب‌ویژن",
            last_synced_at=synced_at,
            payload_json={"needToMerge": False, "rejectTime": None},
        ),
        _make_row(
            KandoJob,
            kando_job_id=2001,
            title="كارشناس پشتيبانی و ارتباط با مشتری",
        ),
        _make_row(
            KandoCandidate,
            kando_candidate_id=501,
            full_name="علی نمونه",
            payload_json={
                "birthDate": "1995-01-01",
                "city": "تهران",
                "email": "ali@example.com",
                "mobile": "09123456789",
            },
        ),
        _make_row(
            KandoCv,
            kando_cv_id=9001,
            kando_candidate_id=501,
            payload_json={
                "aboutMe": "Customer support specialist.",
                "skills": ["CRM", "English"],
                "email": "resume@example.com",
            },
        ),
        _make_row(KandoApplicationSource, kando_application_source_id=1, name="جاب‌ویژن"),
        _make_row(KandoApplicationSource, kando_application_source_id=2, name="Other"),
        _make_row(
            KandoCvWorkExperience,
            kando_cv_id=9001,
            title="Customer Success",
            company_name="B Company",
            payload_json={"achievementsDescription": "Handled chats.", "durationMonths": 12},
        ),
        _make_row(
            KandoCvWorkExperience,
            kando_cv_id=9001,
            title="Customer Support",
            company_name="A Company",
            payload_json={"achievementsDescription": "Handled tickets.", "durationMonths": 24},
        ),
        _make_row(
            KandoCvUniversityDegree,
            kando_cv_id=9001,
            degree_name=None,
            university_name="دانشگاه تهران",
            payload_json={"academicFieldId": 301, "degreeLevelId": 1},
        ),
        _make_row(
            KandoCvLanguageSkill,
            kando_cv_id=9001,
            language_id=1,
            skill_level_id=1,
            payload_json={},
        ),
        _make_row(
            KandoBaseDataCache,
            data_type="languages",
            external_id=1,
            display_name="English",
            payload_json={"titleEn": "English", "titleFa": "انگلیسی"},
        ),
        _make_row(
            KandoBaseDataCache,
            data_type="skill-levels",
            external_id=1,
            display_name="Advanced",
            payload_json={"titleEn": "Advanced", "titleFa": "پیشرفته"},
        ),
        _make_row(
            KandoBaseDataCache,
            data_type="academic-fields",
            external_id=301,
            display_name="زبان انگلیسی",
            payload_json={"titleFa": "زبان انگلیسی"},
        ),
        _make_row(
            KandoBaseDataCache,
            data_type="university-degree-levels",
            external_id=1,
            display_name="Bachelor",
            payload_json={"titleEn": "Bachelor"},
        ),
    ]


def _snapshot(rows: list[object] | None = None) -> dict:
    return SnapshotBuilder(FakeDb(rows or _base_rows())).build_for_kando_application_id(1001).snapshot


def test_snapshot_includes_required_top_level_keys_and_contract_shape() -> None:
    snapshot = _snapshot()

    assert set(snapshot) == {
        "snapshot_version",
        "snapshot_hash",
        "kando",
        "job",
        "candidate",
        "cv",
        "application_sources",
        "work_experiences",
        "education",
        "language_skills",
        "software_skills",
        "missing_fields",
        "metadata",
    }
    assert snapshot["snapshot_version"] == "v1"
    assert snapshot["snapshot_hash"].startswith("sha256:")
    assert snapshot["kando"]["application_id"] == 1001
    assert snapshot["software_skills"] == []


def test_snapshot_can_match_expected_fixture_contract_subset() -> None:
    snapshot = _snapshot()

    assert snapshot["kando"]["application_id"] == 1001
    assert snapshot["job"]["title"] == "کارشناس پشتیبانی و ارتباط با مشتری"
    assert snapshot["candidate"]["full_name"] == "علی نمونه"
    assert snapshot["language_skills"][0]["language"] == "English"


def test_snapshot_hash_is_stable_for_identical_data() -> None:
    rows = _base_rows()

    assert _snapshot(rows)["snapshot_hash"] == _snapshot(rows)["snapshot_hash"]


def test_snapshot_hash_changes_when_relevant_normalized_data_changes() -> None:
    original_hash = _snapshot()["snapshot_hash"]
    rows = _base_rows()
    job = next(row for row in rows if isinstance(row, KandoJob))
    job.title = "Senior Customer Support"

    assert _snapshot(rows)["snapshot_hash"] != original_hash


def test_snapshot_list_ordering_is_deterministic() -> None:
    snapshot = _snapshot()

    assert [item["role_title"] for item in snapshot["work_experiences"]] == [
        "Customer Success",
        "Customer Support",
    ]
    assert snapshot["application_sources"][0]["source_name"] == "جابویژن"


def test_missing_fields_are_captured_without_making_decisions() -> None:
    rows = _base_rows()
    application = next(row for row in rows if isinstance(row, KandoApplication))
    application.kando_cv_id = None
    candidate = next(row for row in rows if isinstance(row, KandoCandidate))
    candidate.payload_json = {}
    cv = next(row for row in rows if isinstance(row, KandoCv))
    cv.payload_json = {}
    job = next(row for row in rows if isinstance(row, KandoJob))
    job.title = None

    missing_fields = _snapshot(rows)["missing_fields"]

    assert "application.cv_id" in missing_fields
    assert "candidate.birth_date" in missing_fields
    assert "candidate.city" in missing_fields
    assert "cv.about_me" in missing_fields
    assert "cv.skills" in missing_fields
    assert "job.title" in missing_fields


def test_contact_data_and_raw_payload_are_excluded_from_ai_safe_snapshot() -> None:
    snapshot = _snapshot()
    serialized = json.dumps(snapshot, ensure_ascii=False)

    assert "ali@example.com" not in serialized
    assert "09123456789" not in serialized
    assert "resume@example.com" not in serialized
    assert "payload_json" not in serialized
    assert "CompanyApiKey" not in serialized


def test_snapshot_builder_does_not_call_kando_client(monkeypatch) -> None:
    from app.services import kando_client

    def fail_if_called(*args, **kwargs):
        raise AssertionError("SnapshotBuilder must not instantiate KandoClient")

    monkeypatch.setattr(kando_client, "KandoClient", fail_if_called)

    assert _snapshot()["kando"]["application_id"] == 1001


def test_application_sources_use_correct_cv_id_and_do_not_use_source_id_as_cv_id() -> None:
    snapshot = _snapshot()

    assert snapshot["application_sources"][0]["cv_id"] == 9001
    assert snapshot["application_sources"][0]["cv_id"] != 1


def test_language_skills_resolve_base_data_language_and_skill_level() -> None:
    snapshot = _snapshot()

    assert snapshot["language_skills"] == [
        {
            "language": "English",
            "language_normalized": "english",
            "level": "Advanced",
            "level_normalized": "advanced",
            "language_id": 1,
            "skill_level_id": 1,
        },
    ]
