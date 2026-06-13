from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import monotonic, sleep
from typing import Any
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.core.errors import ErrorCode, message_fa_for_code

ATS_ENDPOINTS: dict[str, str] = {
    "applications": "/api/v1/Application/GetApplications",
    "application_sources": "/api/v1/Application/GetApplicationSources",
    "application_change_states": "/api/v1/Application/GetApplicationChangeStates",
    "candidates": "/api/v1/Candidate/GetCandidates",
    "candidate_tags": "/api/v1/Candidate/GetCandidateTags",
    "jobs": "/api/v1/Job/GetJobs",
    "hire_steps": "/api/v1/Job/GetHireSteps",
    "cvs": "/api/v1/Cv/GetCvs",
    "cv_work_experiences": "/api/v1/CV/GetCvWorkExperiences",
    "cv_university_degrees": "/api/v1/Cv/GetCvUniversityDegrees",
    "cv_language_skills": "/api/v1/CV/GetCvLanguageSkills",
}

BASEDATA_ENDPOINTS: dict[str, str] = {
    "genders": "/api/v1/genders",
    "military-service-statuses": "/api/v1/military-service-statuses",
    "marital-statuses": "/api/v1/marital-statuses",
    "work-types": "/api/v1/work-types",
    "salary-ranges": "/api/v1/salary-ranges",
    "cities": "/api/v1/cities",
    "job-categories": "/api/v1/job-categories",
    "industries": "/api/v1/industries",
    "seniority-levels": "/api/v1/seniority-levels",
    "academic-fields": "/api/v1/academic-fields",
    "university-degree-levels": "/api/v1/university-degree-levels",
    "languages": "/api/v1/languages",
    "skill-levels": "/api/v1/skill-levels",
    "softwares": "/api/v1/softwares",
}

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS_CODES = {400, 401, 403}
BACKOFF_SECONDS = [0.0, 30.0, 120.0, 600.0]


@dataclass(frozen=True)
class KandoPage:
    endpoint_name: str
    path: str
    page_number: int
    page_size: int
    items: list[dict[str, Any]]
    raw_payload: Any
    total_count: int | None
    status_code: int
    duration_ms: int
    retry_count: int


class KandoClientError(Exception):
    def __init__(
        self,
        *,
        code: ErrorCode,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        self.code = code
        self.message_fa = message_fa_for_code(code)
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(f"{code}: {self.message_fa}")


class KandoClient:
    def __init__(
        self,
        *,
        ats_base_url: str | None = None,
        basedata_base_url: str | None = None,
        api_key: str | None = None,
        api_header_name: str | None = None,
        timeout_seconds: float | None = None,
        default_page_size: int | None = None,
        max_retries: int | None = None,
        transport: httpx.BaseTransport | None = None,
        sleep_func: Callable[[float], None] = sleep,
    ) -> None:
        self._ats_base_url = (ats_base_url or settings.kando_ats_base_url).rstrip("/")
        self._basedata_base_url = (basedata_base_url or settings.kando_basedata_base_url).rstrip("/")
        self._api_key = api_key if api_key is not None else settings.kando_company_api_key
        self._api_header_name = api_header_name or settings.kando_company_api_header_name
        self._timeout_seconds = timeout_seconds or settings.kando_request_timeout_seconds
        self._default_page_size = default_page_size or settings.kando_page_size
        self._max_retries = max(0, max_retries if max_retries is not None else settings.kando_max_retries)
        self._sleep = sleep_func
        self._client = httpx.Client(
            headers={self._api_header_name: self._api_key},
            timeout=httpx.Timeout(self._timeout_seconds),
            transport=transport,
        )

    @property
    def masked_api_key(self) -> str:
        if not self._api_key:
            return "****"
        return f"****{self._api_key[-4:]}"

    def close(self) -> None:
        self._client.close()

    def get_applications(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("applications", page_number, page_size)

    def get_application_sources(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("application_sources", page_number, page_size)

    def get_application_change_states(
        self,
        page_number: int = 1,
        page_size: int | None = None,
    ) -> KandoPage:
        return self._get_ats_page("application_change_states", page_number, page_size)

    def get_candidates(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("candidates", page_number, page_size)

    def get_candidate_tags(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("candidate_tags", page_number, page_size)

    def get_jobs(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("jobs", page_number, page_size)

    def get_hire_steps(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("hire_steps", page_number, page_size)

    def get_cvs(self, page_number: int = 1, page_size: int | None = None) -> KandoPage:
        return self._get_ats_page("cvs", page_number, page_size)

    def get_cv_work_experiences(
        self,
        page_number: int = 1,
        page_size: int | None = None,
    ) -> KandoPage:
        return self._get_ats_page("cv_work_experiences", page_number, page_size)

    def get_cv_university_degrees(
        self,
        page_number: int = 1,
        page_size: int | None = None,
    ) -> KandoPage:
        return self._get_ats_page("cv_university_degrees", page_number, page_size)

    def get_cv_language_skills(
        self,
        page_number: int = 1,
        page_size: int | None = None,
    ) -> KandoPage:
        return self._get_ats_page("cv_language_skills", page_number, page_size)

    def get_base_data(
        self,
        data_type: str,
        page_number: int = 1,
        page_size: int | None = None,
    ) -> KandoPage:
        if data_type not in BASEDATA_ENDPOINTS:
            raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)
        return self._get_page(
            base_url=self._basedata_base_url,
            endpoint_name=f"base_data:{data_type}",
            path=BASEDATA_ENDPOINTS[data_type],
            page_number=page_number,
            page_size=page_size or self._default_page_size,
            include_pagination=False,
        )

    def iter_pages(
        self,
        endpoint_method: Callable[[int, int | None], KandoPage],
        *,
        page_size: int | None = None,
    ) -> Iterable[KandoPage]:
        page_number = 1
        effective_page_size = page_size or self._default_page_size
        while True:
            page = endpoint_method(page_number, effective_page_size)
            yield page
            if not self._has_next_page(page):
                break
            page_number += 1

    def _get_ats_page(
        self,
        endpoint_name: str,
        page_number: int,
        page_size: int | None,
    ) -> KandoPage:
        return self._get_page(
            base_url=self._ats_base_url,
            endpoint_name=endpoint_name,
            path=ATS_ENDPOINTS[endpoint_name],
            page_number=page_number,
            page_size=page_size or self._default_page_size,
            include_pagination=True,
        )

    def _get_page(
        self,
        *,
        base_url: str,
        endpoint_name: str,
        path: str,
        page_number: int,
        page_size: int,
        include_pagination: bool,
    ) -> KandoPage:
        params = {"pageNumber": page_number, "pageSize": page_size} if include_pagination else {}
        started = monotonic()
        response, retry_count = self._get_with_retry(urljoin(f"{base_url}/", path.lstrip("/")), params)
        duration_ms = int((monotonic() - started) * 1000)
        try:
            raw_payload = response.json()
        except ValueError:
            raise KandoClientError(
                code=ErrorCode.KANDO_UNEXPECTED_SCHEMA,
                retryable=False,
            ) from None
        items, total_count = _extract_items(raw_payload)
        return KandoPage(
            endpoint_name=endpoint_name,
            path=path,
            page_number=page_number,
            page_size=page_size,
            items=items,
            raw_payload=raw_payload,
            total_count=total_count,
            status_code=response.status_code,
            duration_ms=duration_ms,
            retry_count=retry_count,
        )

    def _get_with_retry(
        self,
        url: str,
        params: dict[str, int],
    ) -> tuple[httpx.Response, int]:
        retry_count = 0
        for attempt in range(self._max_retries + 1):
            if attempt:
                retry_count += 1
                self._sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
            try:
                response = self._client.get(url, params=params)
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException):
                if attempt >= self._max_retries:
                    raise KandoClientError(
                        code=ErrorCode.KANDO_TIMEOUT,
                        retryable=True,
                    ) from None
                continue
            except httpx.TransportError:
                if attempt >= self._max_retries:
                    raise KandoClientError(
                        code=ErrorCode.KANDO_UNAVAILABLE,
                        retryable=True,
                    ) from None
                continue

            if response.status_code in NON_RETRYABLE_STATUS_CODES:
                raise _error_for_response(response)
            if response.status_code in RETRYABLE_STATUS_CODES:
                if attempt >= self._max_retries:
                    raise _error_for_response(response)
                continue
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                raise _error_for_response(response) from None
            return response, retry_count

        raise KandoClientError(code=ErrorCode.KANDO_UNAVAILABLE, retryable=True)

    def _has_next_page(self, page: KandoPage) -> bool:
        if not page.items:
            return False
        if page.total_count is not None:
            return page.page_number * page.page_size < page.total_count
        return len(page.items) >= page.page_size


def _extract_items(payload: Any) -> tuple[list[dict[str, Any]], int | None]:
    total_count = _extract_total_count(payload)
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = None
        for key in ("data", "items", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                items = value
                break
        if items is None:
            raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)
    else:
        raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)

    if not all(isinstance(item, dict) for item in items):
        raise KandoClientError(code=ErrorCode.KANDO_UNEXPECTED_SCHEMA, retryable=False)
    return items, total_count


def _extract_total_count(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    for key in ("totalCount", "total_count", "total"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
    return None


def _error_for_response(response: httpx.Response) -> KandoClientError:
    if response.status_code in {401, 403}:
        return KandoClientError(
            code=ErrorCode.KANDO_AUTH_FAILED,
            status_code=response.status_code,
            retryable=False,
        )
    if response.status_code == 429:
        return KandoClientError(
            code=ErrorCode.KANDO_RATE_LIMITED,
            status_code=response.status_code,
            retryable=True,
        )
    if response.status_code == 408:
        return KandoClientError(
            code=ErrorCode.KANDO_TIMEOUT,
            status_code=response.status_code,
            retryable=True,
        )
    if response.status_code in {500, 502, 503, 504}:
        return KandoClientError(
            code=ErrorCode.KANDO_UNAVAILABLE,
            status_code=response.status_code,
            retryable=True,
        )
    return KandoClientError(
        code=ErrorCode.KANDO_UNEXPECTED_SCHEMA,
        status_code=response.status_code,
        retryable=False,
    )
