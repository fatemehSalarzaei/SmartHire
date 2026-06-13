ROLE_CODES = (
    "SUPER_ADMIN",
    "SYSTEM_ADMIN",
    "HR_MANAGER",
    "RECRUITER",
    "REVIEWER",
    "READ_ONLY_AUDITOR",
)

PERMISSION_CODES = (
    "view_applications",
    "view_sensitive_contact",
    "create_recruiter_note",
    "create_recruiter_decision",
    "manage_ruleset_draft",
    "activate_ruleset",
    "admin_reprocess",
    "access_sqladmin",
    "view_raw_payload",
    "view_ai_raw_output",
    "change_kando_settings",
)

ROLE_PERMISSIONS = {
    "SUPER_ADMIN": PERMISSION_CODES,
    "SYSTEM_ADMIN": PERMISSION_CODES,
    "HR_MANAGER": (
        "view_applications",
        "view_sensitive_contact",
        "create_recruiter_note",
        "create_recruiter_decision",
        "manage_ruleset_draft",
        "activate_ruleset",
    ),
    "RECRUITER": (
        "view_applications",
        "create_recruiter_note",
        "create_recruiter_decision",
    ),
    "REVIEWER": (
        "view_applications",
        "create_recruiter_note",
        "create_recruiter_decision",
    ),
    "READ_ONLY_AUDITOR": (
        "view_applications",
    ),
}
