from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

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
        model="gpt-5.4-mini-2026-03-17",
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
    spans = result.provider_response["provider_attempt_spans"]
    assert len(spans) == 1
    assert spans[0]["schema_version"] == "apps_rg_provider_attempt_span_v1"
    assert spans[0]["provider"] == "external_openai"
    assert spans[0]["provider_attempted"] is False
    assert spans[0]["runtime_generation_status"] == "BLOCKED"
    assert spans[0]["duration_seconds"] is not None


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
    spans = result.provider_response["provider_attempt_spans"]
    assert len(spans) == 1
    assert spans[0]["provider"] == "external_openai"
    assert spans[0]["model"] == "external-test-model"
    assert spans[0]["runtime_generation_status"] == "REAL_LLM"
    assert spans[0]["timeout_seconds"] == 6.5
    assert spans[0]["token_budget"] == 88
    assert result.provider_response["provider_attempt_timing_summary"]["span_count"] == 1
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
        model="gpt-5.4-mini-2026-03-17",
        transport=lambda _request: (_ for _ in ()).throw(OSError("down")),
        environ={"OPENAI_API_KEY": "test-key"},
    )

    result = provider.generate(_compiled_prompt(), token_budget=10)

    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is True
    assert result.provider_available is False
    assert "ProviderGatewayError" in str(result.exact_provider_error)
    assert result.provider_response is not None
    assert result.provider_response["attempt_started_at_utc"]
    assert result.provider_response["attempt_completed_at_utc"]
    span = result.provider_response["provider_attempt_spans"][0]
    assert span["provider_attempted"] is True
    assert span["provider_available"] is False
    assert span["runtime_generation_status"] == "BLOCKED"
    assert "ProviderGatewayError" in span["exact_provider_error"]


def test_external_provider_json_errors_fail_closed() -> None:
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model="gpt-5.4-mini-2026-03-17",
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


def test_anthropic_messages_transport_omits_temperature_for_sonnet5(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _StreamResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def __iter__(self):
            return iter(
                [
                    b'data: {"type":"message_start","message":{"model":"claude-sonnet-5"}}\n',
                    b'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"{}"}}\n',
                    b'data: {"type":"message_stop"}\n',
                ]
            )

    def _urlopen(req, timeout):
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _StreamResponse()

    monkeypatch.setattr(subject.urllib.request, "urlopen", _urlopen)
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
        model="claude-sonnet-5",
        environ={"ANTHROPIC_API_KEY": "test-key"},
    )

    response = provider._anthropic_messages_transport(
        {"prompt": "Return JSON", "max_tokens": 20, "temperature": 0.4}
    )

    assert response["text"] == "{}"
    assert captured["body"]["model"] == "claude-sonnet-5"
    assert "temperature" not in captured["body"]


def test_anthropic_messages_transport_keeps_temperature_for_sonnet4(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _StreamResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def __iter__(self):
            return iter(
                [
                    b'data: {"type":"message_start","message":{"model":"claude-sonnet-4-6"}}\n',
                    b'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"{}"}}\n',
                    b'data: {"type":"message_stop"}\n',
                ]
            )

    def _urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _StreamResponse()

    monkeypatch.setattr(subject.urllib.request, "urlopen", _urlopen)
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
        model="claude-sonnet-4-6",
        environ={"ANTHROPIC_API_KEY": "test-key"},
    )

    provider._anthropic_messages_transport(
        {"prompt": "Return JSON", "max_tokens": 20, "temperature": 0.4}
    )

    assert captured["body"]["temperature"] == 0.4


def test_external_provider_requires_explicit_model() -> None:
    with pytest.raises(Exception, match="requires an explicit model"):
        ExternalProvider(provider_profile=ProviderProfile.EXTERNAL_OPENAI, environ={})
