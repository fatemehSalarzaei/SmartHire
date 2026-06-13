# Normalization Spec

## Persian text

- Convert Arabic `ي` to Persian `ی`.
- Convert Arabic `ك` to Persian `ک`.
- Normalize whitespace.
- Remove unnecessary zero-width characters.
- Remove punctuation for matching, but preserve original text.
- Lowercase English.

## Aliases

Maintain aliases in `screening_rule_terms.aliases_json`.

Examples:

| Canonical | Aliases |
|---|---|
| دانشگاه صنعتی شریف | شریف، صنعتی شریف، Sharif، SUT |
| دانشگاه تهران | تهران، University of Tehran، UT |
| Customer Support | پشتیبانی مشتری، کارشناس پشتیبانی، support specialist |

## Do not normalize away meaning

Keep original fields for audit and display. Use normalized value only for matching.
