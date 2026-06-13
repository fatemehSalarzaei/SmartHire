import inspect

import httpx
import pytest

from app.core.errors import ErrorCode, message_fa_for_code
from app.services.kando_client import KandoClient, KandoClientError


def _json_response(status_code: int, payload):
    return httpx.Response(status_code, json=payload)


def test_kando_client_exposes_no_public_write_or_generic_request_methods() -> None:
    public_callables = {
        name
        for name, value in inspect.getmembers(KandoClient)
        if not name.startswith("_") and callable(value)
    }

    assert "request" not in public_callables
    assert "post" not in public_callables
    assert "put" not in public_callables
    assert "patch" not in public_callables
    assert "delete" not in public_callables


def test_public_kando_endpoint_methods_use_get_only() -> None:
    seen_methods: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_methods.append(request.method)
        return _json_response(200, [])

    client = KandoClient(
        api_key="super-secret-key",
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    client.get_applications()
    client.get_application_sources()
    client.get_application_change_states()
    client.get_candidates()
    client.get_candidate_tags()
    client.get_jobs()
    client.get_hire_steps()
    client.get_cvs()
    client.get_cv_work_experiences()
    client.get_cv_university_degrees()
    client.get_cv_language_skills()
    client.get_base_data("industries")

    assert seen_methods
    assert set(seen_methods) == {"GET"}


def test_api_key_is_not_leaked_in_error_text() -> None:
    secret = "super-secret-kando-key"

    def handler(request: httpx.Request) -> httpx.Response:
        return _json_response(401, {"error": f"bad key {secret}"})

    client = KandoClient(
        api_key=secret,
        max_retries=0,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    with pytest.raises(KandoClientError) as exc_info:
        client.get_jobs()

    assert exc_info.value.code == ErrorCode.KANDO_AUTH_FAILED
    assert secret not in str(exc_info.value)
    assert client.masked_api_key == "****-key"


def test_retry_occurs_on_retryable_status_code() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return _json_response(500, {"error": "temporary"})
        return _json_response(200, [{"jobId": 1, "title": "Support"}])

    client = KandoClient(
        max_retries=2,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    page = client.get_jobs()

    assert calls == 2
    assert page.retry_count == 1
    assert page.items == [{"jobId": 1, "title": "Support"}]


@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_retry_does_not_occur_on_non_retryable_status_codes(status_code: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _json_response(status_code, {"error": "stop"})

    client = KandoClient(
        max_retries=3,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    with pytest.raises(KandoClientError):
        client.get_jobs()

    assert calls == 1


def test_retry_occurs_on_timeout() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("timeout")
        return _json_response(200, [])

    client = KandoClient(
        max_retries=1,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    page = client.get_jobs()

    assert calls == 2
    assert page.retry_count == 1


def test_pagination_fetches_more_than_one_page() -> None:
    seen_pages: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        page_number = request.url.params["pageNumber"]
        seen_pages.append(page_number)
        if page_number == "1":
            return _json_response(200, {"data": [{"jobId": 1}], "totalCount": 2})
        return _json_response(200, {"data": [{"jobId": 2}], "totalCount": 2})

    client = KandoClient(
        default_page_size=1,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    pages = list(client.iter_pages(client.get_jobs, page_size=1))

    assert seen_pages == ["1", "2"]
    assert [item["jobId"] for page in pages for item in page.items] == [1, 2]


def test_unexpected_schema_maps_to_persian_message_without_retry() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _json_response(200, {"unexpected": "shape"})

    client = KandoClient(
        max_retries=3,
        transport=httpx.MockTransport(handler),
        sleep_func=lambda seconds: None,
    )

    with pytest.raises(KandoClientError) as exc_info:
        client.get_jobs()

    assert calls == 1
    assert exc_info.value.code == ErrorCode.KANDO_UNEXPECTED_SCHEMA
    assert exc_info.value.message_fa == message_fa_for_code(ErrorCode.KANDO_UNEXPECTED_SCHEMA)
