import re
import string
from typing import Any

ARABIC_TO_PERSIAN = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
    },
)

ZERO_WIDTH_CHARS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u200e",
    "\u200f",
    "\ufeff",
}

PERSIAN_ARABIC_PUNCTUATION = "،؛؟«»"
MATCHING_PUNCTUATION = string.punctuation + PERSIAN_ARABIC_PUNCTUATION


class NormalizationService:
    def normalize_display_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.translate(ARABIC_TO_PERSIAN)
        normalized = self._remove_zero_width(normalized)
        normalized = self._normalize_whitespace(normalized)
        return normalized or None

    def normalize_for_matching(self, value: str | None) -> str | None:
        display_value = self.normalize_display_text(value)
        if display_value is None:
            return None
        lowered = display_value.lower()
        punctuation_table = str.maketrans({char: " " for char in MATCHING_PUNCTUATION})
        without_punctuation = lowered.translate(punctuation_table)
        return self._normalize_whitespace(without_punctuation) or None

    def normalize_string_list(self, values: Any) -> list[str]:
        if not isinstance(values, list):
            return []
        normalized_values = []
        for value in values:
            if isinstance(value, str):
                normalized = self.normalize_display_text(value)
                if normalized:
                    normalized_values.append(normalized)
        return normalized_values

    def _remove_zero_width(self, value: str) -> str:
        return "".join(char for char in value if char not in ZERO_WIDTH_CHARS)

    def _normalize_whitespace(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
