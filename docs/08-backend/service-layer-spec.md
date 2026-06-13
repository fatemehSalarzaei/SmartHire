# Service Layer Spec

## Required services

| Service | Responsibility |
|---|---|
| `KandoClient` | Low-level read-only Kando GET calls |
| `KandoSyncService` | Sync orchestration and persistence |
| `SnapshotBuilder` | Build canonical application snapshot |
| `NormalizationService` | Persian/English normalization and alias matching |
| `AIAnalysisService` | Prompt, call LLM, validate output |
| `RuleEngine` | Deterministic internal decision |
| `RankingEngine` | Score, bucket and rank |
| `NoteGenerator` | Generate Persian internal notes |
| `AuditService` | Immutable audit logs |
| `PermissionService` | RBAC checks |

## Transaction rules

- Sync writes raw payload and normalized data in controlled transactions.
- Decision writes should be atomic: decision + score + note + audit.
- Long-running external calls should not hold DB transaction open.
