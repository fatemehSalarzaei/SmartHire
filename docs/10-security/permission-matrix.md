# Permission Matrix

| Action | SUPER_ADMIN | SYSTEM_ADMIN | HR_MANAGER | RECRUITER | REVIEWER | READ_ONLY_AUDITOR |
|---|---|---|---|---|---|---|
| View applications | yes | yes | yes | yes | yes | yes |
| View sensitive contact | yes | yes | yes | conditional | no | no |
| Create recruiter note | yes | yes | yes | yes | yes | no |
| Create recruiter decision | yes | yes | yes | yes | yes | no |
| Manage RuleSet draft | yes | yes | yes | no | no | no |
| Activate RuleSet | yes | yes | yes | no | no | no |
| Admin reprocess | yes | yes | no | no | no | no |
| Access SQLAdmin | yes | yes | no | no | no | audit-only if configured |
| View raw payload | yes | yes | no | no | no | limited |
| View AI raw output | yes | yes | no | no | no | no |
| Change Kando settings | yes | yes | no | no | no | no |
