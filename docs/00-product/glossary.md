# Glossary

| Term | Meaning |
|---|---|
| Kando | External ATS data source. Read-only in Phase 1. |
| SmartHire | Internal platform that stores decisions, notes, scores and recruiter workflow. |
| Application | Candidate application for a Kando job. |
| CV Snapshot | Normalized, immutable input object assembled from Kando structured data for analysis. |
| RuleSet | Versioned rules attached to a Kando job. |
| Rule Engine | Deterministic engine that produces internal decision and reasons. |
| Ranking Engine | Deterministic engine that produces score, bucket and rank. |
| AI Analysis | Assistive analysis layer that extracts signals and summaries; not final decision-maker. |
| Internal Status | SmartHire-only application status such as `SMART_REJECTED`. |
| Recruiter Decision | Human decision recorded in SmartHire after reviewing the assistant output. |
| SQLAdmin | Technical admin UI mounted on `/admin`; not HR panel. |
