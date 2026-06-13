# Kando API Contract

Kando is read-only in Phase 1.

## Auth

```http
CompanyApiKey: <secret-api-key>
```

## Base URLs

```env
KANDO_ATS_BASE_URL=https://atsedgeapi.hrcando.ir
KANDO_BASEDATA_BASE_URL=https://basedataapinew.hrcando.ir
```

## ATS Edge endpoints from supplied Postman collection

| Method | Endpoint | Name |
|---|---|---|
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Application/GetApplications?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Application/GetApplications |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Application/GetApplicationSources?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Application/GetApplicationSources |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Application/GetApplicationChangeStates?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Application/GetApplicationChangeStates |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Candidate/GetCandidates?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Candidate/GetCandidates |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Candidate/GetCandidateTags?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Candidate/GetCandidateTags |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetBranches?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Company/GetBranches |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetDepartments?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Company/GetDepartments |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetAddresses?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Company/GetAddresses |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetRejectReasons?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Company/GetRejectReasons |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetRoles?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Company/GetRoles |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetSources?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Company/GetSources |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Company/GetTags?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Company/GetTags |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Cv/GetCvs?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Cv/GetCvs |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/CV/GetCvWorkExperiences?pageSize={{page_size}}&pageNumber={{page_number}}` | /api/v1/Cv/GetCvWorkExperiences |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Cv/GetCvUniversityDegrees?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Cv/GetCvUniversityDegrees |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/CV/GetCvSoftwareSkills?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Cv/GetCvSoftwareSkills |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/CV/GetCvLanguageSkills?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Cv/GetCvLanguageSkills |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Interview/GetInterviews?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Interview/GetInterviews |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Interview/GetInterviewers?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Interview/GetInterviewers |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Interview/GetOnlineInterviews?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Interview/GetOnlineInterviews |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Job/GetJobs?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Job/GetJobs |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Job/GetHireSteps?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Job/GetHireSteps |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Job/GetHireStepSubCategories?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Job/GetHireStepSubCategories |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Job/GetJobLogs?pageNumber={{page_number}}&pageSize={{page_size}}` | /api/v1/Job/GetJobLogs |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Operator/GetOperators?pageNumber={{page_number}}&pageSize={{page_size}}` | GetOperators |
| `GET` | `KANDO_ATS_BASE_URL/api/v1/Operator/GetOperatorRoleBranches?pageNumber={{page_number}}&pageSize={{page_size}}` | Get Operator Role Branches |

## BaseData endpoints from supplied Postman collection

| Method | Endpoint | Name |
|---|---|---|
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/genders` | Genders |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/military-service-statuses` | Military Service Statuses |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/marital-statuses` | Marital Statuses |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/work-types` | Work Types |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/salary-ranges` | Salary Ranges |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/countires/:countryId/states` | States |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/cities` | Cities |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/cities/:cityid/regions` | Regions |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/job-categories` | Job Categories |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/industries` | Industries |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/seniority-levels` | Seniority Levels |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/academic-fields` | Academic Fields |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/university-degree-levels` | University Degree Levels |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/languages` | Languages |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/skill-levels` | Skill Levels |
| `GET` | `KANDO_BASEDATA_BASE_URL/api/v1/softwares` | Softwares |

## Implementation rules

- Use `httpx`.
- All requests must have timeout.
- All list endpoints must support pagination.
- Store raw response in `kando_raw_payloads`.
- Normalize into internal tables.
- Do not expose API key in logs.
- Do not call write endpoints.
