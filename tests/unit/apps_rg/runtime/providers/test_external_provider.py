from __future__ import annotations

import json
import urllib.error
from types import SimpleNamespace

from apps_rg.runtime.providers import external_provider as subject
from apps_rg.runtime.providers.external_provider import ExternalProvider
from apps_rg.runtime.providers.provider_gateway import ProviderProfile


def _compiled_prompt() -> SimpleNamespace:
    return SimpleNamespace(
        prompt_blocks=(
            SimpleNamespace(role="system", content="System guard."),
            SimpleNamespace(role="user", content="Write one bullet."),
        ),
        system_preamble="Fallback system",
        user_instruction="Fallback user",
    )


def test_prompt_text_prefers_prompt_blocks() -> None:
    assert subject._prompt_text(_compiled_prompt()) == (
        "system: System guard.\nuser: Write one bullet."
    )


def test_prompt_text_falls_back_to_preamble_and_instruction() -> None:
    compiled = SimpleNamespace(
        prompt_blocks=(),
        system_preamble="System preamble.",
        user_instruction="User instruction.",
    )

    assert subject._prompt_text(compiled) == "System preamble.\nUser instruction."


def test_coerce_timeout_seconds_uses_default_for_invalid_values() -> None:
    assert subject._coerce_timeout_seconds("12.5") == 12.5
    assert subject._coerce_timeout_seconds(None) == subject.DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    assert subject._coerce_timeout_seconds("bad") == subject.DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    assert subject._coerce_timeout_seconds(0) == subject.DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    assert subject._coerce_timeout_seconds(-1) == subject.DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS


def test_external_provider_blocks_without_credentials_and_does_not_call_transport() -> None:
    def _transport(_request):
        raise AssertionError("transport should not be called without credentials")

    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=_transport,
        environ={},
    )

    result = provider.generate(_compiled_prompt(), token_budget=50)

    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is False
    assert result.provider_available is False
    assert "OPENAI_API_KEY" in str(result.exact_provider_error)
    assert result.provider_response is not None
    assert result.provider_response["attempt_started_at_utc"]
    assert result.provider_response["attempt_completed_at_utc"]


def test_external_provider_threads_request_to_injected_transport() -> None:
    captured: dict[str, object] = {}

    def _transport(request):
        captured.update(request)
        return {"text": "Generated section.", "model": "external-test-model"}

    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model="external-test-model",
        base_url="https://provider.example.test/responses",
        transport=_transport,
        environ={"OPENAI_API_KEY": "test-key"},
    )

    result = provider.generate(
        _compiled_prompt(),
        token_budget=88,
        temperature=0.21,
        timeout_seconds="6.5",
    )

    assert result.runtime_generation_status == "REAL_LLM"
    assert result.raw_model_output == "Generated section."
    assert result.provider_requested == "external_openai"
    assert result.model == "external-test-model"
    assert result.provider_response is not None
    assert result.provider_response["request_digest"]
    assert result.provider_response["attempt_started_at_utc"]
    assert result.provider_response["attempt_completed_at_utc"]
    assert result.provider_response["transport_response"]["text"] == "Generated section."
    assert captured == {
        "provider_profile": "external_openai",
        "model": "external-test-model",
        "prompt": "system: System guard.\nuser: Write one bullet.",
        "max_tokens": 88,
        "temperature": 0.21,
        "base_url": "https://provider.example.test/responses",
        "timeout_seconds": 6.5,
        "progress_sink": {},
    }


def test_external_provider_transport_errors_fail_closed() -> None:
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=lambda _request: (_ for _ in ()).throw(urllib.error.URLError("down")),
        environ={"OPENAI_API_KEY": "test-key"},
    )

    result = provider.generate(_compiled_prompt(), token_budget=10)

    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is True
    assert result.provider_available is False
    assert "URLError" in str(result.exact_provider_error)
    assert result.provider_response is not None
    assert result.provider_response["attempt_started_at_utc"]
    assert result.provider_response["attempt_completed_at_utc"]


def test_external_provider_json_errors_fail_closed() -> None:
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=lambda _request: (_ for _ in ()).throw(
            json.JSONDecodeError("bad", "{}", 0)
        ),
        environ={"OPENAI_API_KEY": "test-key"},
    )

    result = provider.generate(_compiled_prompt(), token_budget=10)

    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is True
    assert result.provider_available is False
    assert "JSONDecodeError" in str(result.exact_provider_error)
