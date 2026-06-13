# Kando Field Mapping

## Key mapping

| Kando source | Internal model/field | Notes |
|---|---|---|
| `Job.jobId` | `kando_jobs.kando_job_id` | External job key |
| `Job.title` | `kando_jobs.title` | Display title |
| `Application.applicationId` | `kando_applications.kando_application_id` | External application key |
| `Application.candidateId` | `kando_applications.kando_candidate_id` | External candidate key |
| `Application.jobId` | `kando_applications.kando_job_id` | Job relation |
| `Application.hireStepId` | `kando_applications.kando_hire_step_id` | Read-only current Kando step |
| `Application.statusId` | `kando_applications.kando_status_id` | Read-only current Kando status |
| `Application.needToMerge` | `kando_applications.need_to_merge` | Default `NEEDS_HUMAN_REVIEW` signal |
| `Application.rejectTime` | `kando_applications.kando_reject_time` | Do not auto-screen unless policy allows |
| `ApplicationSource.cvId` | `kando_application_sources.kando_cv_id` | Main CV key |
| `ApplicationSource.coverLetter` | Snapshot `application_sources[].cover_letter` | May be sent to AI if allowed |
| `ApplicationSource.jobBoardCompanyName` | `source_name` | Candidate source label |
| `ApplicationSource.totalWorkExperienceTimeSpan` | `total_work_experience_months` | Normalize to months if possible |
| `Candidate.birthDate` | Snapshot `candidate.birth_date`, derived `candidate.age` | Missing => `NEEDS_HUMAN_REVIEW` |
| `Candidate.email` | `candidate.email` | Sensitive |
| `Candidate.mobile` | `candidate.phone` | Sensitive |
| `Cv.aboutMe` | Snapshot `cv.about_me` | AI and text match source |
| `Cv.skills` | Snapshot `cv.skills` | AI and text match source |
| `CvWorkExperience.roleTitle` | Snapshot `work_experiences[].role_title` | Rule and AI source |
| `CvWorkExperience.achievementsDescription` | Snapshot `work_experiences[].description` | Rule and AI source |
| `CvWorkExperience.jobCategoryId` | BaseData lookup `job_categories` | Normalize title |
| `CvUniversityDegree.universityName` | Snapshot `education[].university_name` | Fuzzy match |
| `CvUniversityDegree.academicFieldId` | BaseData lookup `academic_fields` | Normalize field title |
| `CvLanguageSkill.languageId` | BaseData lookup `languages` | English detection |
| `CvLanguageSkill.skillLevelId` | BaseData lookup `skill_levels` | Advanced/Intermediate/Beginner |

## Derived fields

- `candidate.age`
- `language.english_level`
- `snapshot_hash`
- `missing_fields`
- `has_related_experience_structured`
- `has_target_education`
