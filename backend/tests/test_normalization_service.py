from app.services.normalization_service import NormalizationService


def test_persian_arabic_text_normalization_preserves_display_meaning() -> None:
    service = NormalizationService()

    assert service.normalize_display_text("  كارشناس\u200c پشتيبانی  ") == "کارشناس پشتیبانی"


def test_matching_normalization_lowercases_english_and_removes_punctuation() -> None:
    service = NormalizationService()

    assert service.normalize_for_matching("Customer-Support, CRM!") == "customer support crm"


def test_normalize_string_list_preserves_original_display_values() -> None:
    service = NormalizationService()

    assert service.normalize_string_list([" CRM ", "پشتيبانی"]) == ["CRM", "پشتیبانی"]
