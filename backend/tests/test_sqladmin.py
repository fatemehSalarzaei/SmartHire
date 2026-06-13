from __future__ import annotations

from app.admin.masking import MASK, mask_json, mask_secret
from app.admin.security import evaluate_sqladmin_access
from app.admin.views import (
    ADMIN_VIEWS,
    AIAnalysisResultAdmin,
    AuditLogAdmin,
    KandoConnectionAdmin,
    KandoRawPayloadAdmin,
    ScreeningApplicationAdmin,
    ScreeningRuleAdmin,
    ScreeningRuleGroupAdmin,
    ScreeningRuleSetAdmin,
    ScreeningRuleTermAdmin,
    UserAdmin,
)


def test_sqladmin_access_is_limited_to_technical_roles() -> None:
    assert evaluate_sqladmin_access({"SUPER_ADMIN"}).allowed is True
    assert evaluate_sqladmin_access({"SUPER_ADMIN"}).read_only is False
    assert evaluate_sqladmin_access({"SYSTEM_ADMIN"}).allowed is True
    assert evaluate_sqladmin_access({"TECH_SUPPORT"}).allowed is True
    assert evaluate_sqladmin_access({"TECH_SUPPORT"}).read_only is True
    assert evaluate_sqladmin_access({"READ_ONLY_AUDITOR"}).allowed is True
    assert evaluate_sqladmin_access({"READ_ONLY_AUDITOR"}).read_only is True

    for hr_role in ("HR_MANAGER", "RECRUITER", "REVIEWER"):
        access = evaluate_sqladmin_access({hr_role})
        assert access.allowed is False
        assert access.read_only is True


def test_sqladmin_editable_and_read_only_boundaries_are_declared() -> None:
    assert UserAdmin.can_create is True
    assert UserAdmin.can_edit is True
    assert UserAdmin.can_delete is True

    for view in (
        KandoRawPayloadAdmin,
        ScreeningApplicationAdmin,
        AIAnalysisResultAdmin,
        AuditLogAdmin,
    ):
        assert view.can_create is False
        assert view.can_edit is False
        assert view.can_delete is False

    for view in (
        ScreeningRuleSetAdmin,
        ScreeningRuleGroupAdmin,
        ScreeningRuleAdmin,
        ScreeningRuleTermAdmin,
    ):
        assert view.can_create is True
        assert view.can_edit is True
        assert view.can_delete is True


def test_sqladmin_registers_expected_model_views() -> None:
    names = {view.__name__ for view in ADMIN_VIEWS}
    assert "UserAdmin" in names
    assert "KandoConnectionAdmin" in names
    assert "KandoRawPayloadAdmin" in names
    assert "ScreeningDecisionAdmin" in names
    assert "RankingResultAdmin" in names
    assert "AIAnalysisRunAdmin" in names
    assert "AuditLogAdmin" in names
    assert "IntegrationErrorAdmin" in names


def test_sqladmin_masks_secrets_and_nested_sensitive_json() -> None:
    assert mask_secret("short") == MASK
    assert mask_secret("abcd1234efgh") == "abcd…efgh"

    masked = mask_json(
        {
            "CompanyApiKey": "secret",
            "nested": {
                "authorization": "Bearer token",
                "safe": "value",
                "candidate": {"email": "candidate@example.com", "full_name": "Candidate"},
            },
        },
    )

    assert masked["CompanyApiKey"] == MASK
    assert masked["nested"]["authorization"] == MASK
    assert masked["nested"]["safe"] == "value"
    assert masked["nested"]["candidate"]["email"] == MASK
    assert masked["nested"]["candidate"]["full_name"] == "Candidate"


def test_sqladmin_sensitive_columns_are_not_exported() -> None:
    excluded = {getattr(column, "key", str(column)) for column in KandoConnectionAdmin.column_export_exclude_list}
    assert "encrypted_api_key" in excluded

    raw_excluded = {getattr(column, "key", str(column)) for column in KandoRawPayloadAdmin.column_export_exclude_list}
    assert "payload_json" in raw_excluded

    ai_excluded = {getattr(column, "key", str(column)) for column in AIAnalysisResultAdmin.column_export_exclude_list}
    assert "output_json" in ai_excluded
