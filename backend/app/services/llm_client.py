from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

AI_UNAVAILABLE_CODE = "AI_ANALYSIS_UNAVAILABLE"
AI_UNAVAILABLE_MESSAGE_FA = (
    "تحلیل هوش مصنوعی در حال حاضر در دسترس نیست. رزومه با قوانین ساختاریافته بررسی شد."
)


@dataclass(frozen=True)
class LLMRequest:
    system_message: str
    user_message: str
    prompt_version: str
    response_format: str = "json"


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model_name: str


class LLMProviderError(Exception):
    def __init__(
        self,
        *,
        code: str = AI_UNAVAILABLE_CODE,
        message_fa: str = AI_UNAVAILABLE_MESSAGE_FA,
        retryable: bool = True,
    ) -> None:
        self.code = code
        self.message_fa = message_fa
        self.retryable = retryable
        super().__init__(code)


class LLMProvider(Protocol):
    provider_name: str
    model_name: str

    def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError


class DisabledLLMProvider:
    provider_name = "disabled"
    model_name = "none"

    def complete(self, request: LLMRequest) -> LLMResponse:
        raise LLMProviderError()


class HttpJsonLLMProvider:
    """Minimal HTTP JSON provider for future production wiring.

    The implementation is intentionally small and explicit. Tests use fake providers;
    this provider is not required to contact a real LLM during Task 06 validation.
    """

    def __init__(
        self,
        *,
        endpoint_url: str,
        api_key: str | None = None,
        provider_name: str = "http_json",
        model_name: str = "default",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.provider_name = provider_name
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def complete(self, request: LLMRequest) -> LLMResponse:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            response = httpx.post(
                self.endpoint_url,
                headers=headers,
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": request.system_message},
                        {"role": "user", "content": request.user_message},
                    ],
                    "response_format": {"type": "json_object"},
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError() from exc

        payload = response.json()
        content = _extract_content(payload)
        if not content:
            raise LLMProviderError(retryable=False)
        return LLMResponse(content=content, provider=self.provider_name, model_name=self.model_name)


class LLMClient:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or DisabledLLMProvider()

    @property
    def provider_name(self) -> str:
        return self.provider.provider_name

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    def complete(self, request: LLMRequest) -> LLMResponse:
        return self.provider.complete(request)


def _extract_content(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("content"), str):
        return payload["content"]
    if isinstance(payload.get("response"), str):
        return payload["response"]
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    return None
