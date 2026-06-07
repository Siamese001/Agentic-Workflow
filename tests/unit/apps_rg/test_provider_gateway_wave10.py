"""Wave 10A apps_rg provider gateway tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.providers import (
    ExternalProvider,
    ProviderGateway,
    ProviderProfile,
    ProviderProfileNotRegisteredError,
    QwenVLLMProvider,
    load_provider_profiles_config,
    resolve_provider_profile,
)
from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult


def _prompt() -> SimpleNamespace:
    return SimpleNamespace(
        request_id="req-1",
        run_id="run-1",
        compilation_hash="abc123",
        prompt_blocks=(),
        system_preamble="System",
        user_instruction="Write a concise resume section.",
    )


def test_wave10a_provider_profiles_config_keeps_qwen_default() -> None:
    data = load_provider_profiles_config()
    assert data["wave10a_policy"]["default_provider"] == "qwen_vllm"
    assert data["wave10a_policy"]["external_default_status"] == "selectable_for_parity_not_default"
    profiles = data["profiles"]
    assert profiles["local_qwen_generator"]["default"] is True
    assert profiles["local_qwen_generator"]["provider_profile"] == "qwen_vllm"
    assert profiles["external_openai_generator"]["default"] is False
    assert profiles["external_claude_generator"]["default"] is False


def test_wave10a_provider_profile_resolution_defaults_to_qwen(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_PROVIDER_PROFILE", raising=False)
    selected = resolve_provider_profile()
    assert selected.profile == ProviderProfile.QWEN_VLLM
    assert selected.source == "wave10a_default_qwen_vllm"


def test_wave10a_provider_profile_env_selects_external(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_PROVIDER_PROFILE", "external_openai")
    selected = resolve_provider_profile()
    assert selected.profile == ProviderProfile.EXTERNAL_OPENAI
    assert selected.source == "APPS_RG_PROVIDER_PROFILE"


def test_provider_gateway_dispatches_registered_provider() -> None:
    class _Provider:
        provider_profile = ProviderProfile.QWEN_VLLM

        def generate(self, compiled_prompt, *, token_budget: int, temperature: float = 0.7):
            return ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status="REAL_LLM",
                model="m",
                raw_model_output=f"{compiled_prompt.run_id}:{token_budget}:{temperature}",
                provider_response={},
            )

    gateway = ProviderGateway({ProviderProfile.QWEN_VLLM: _Provider()})
    result = gateway.generate(ProviderProfile.QWEN_VLLM, _prompt(), token_budget=123, temperature=0.2)
    assert result.raw_model_output == "run-1:123:0.2"


def test_provider_gateway_blocks_unregistered_profile() -> None:
    gateway = ProviderGateway()
    with pytest.raises(ProviderProfileNotRegisteredError):
        gateway.generate(ProviderProfile.EXTERNAL_OPENAI, _prompt(), token_budget=10)


def test_qwen_provider_wrapper_delegates_to_existing_transport(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _fake_call(payload, *, base_url: str, timeout: int | None = None):
        captured["payload"] = payload
        captured["base_url"] = base_url
        captured["timeout"] = timeout
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model=str(payload["model"]),
            raw_model_output='{"ok": true}',
            provider_response={"stub": False},
        )

    monkeypatch.setattr("apps_rg.runtime.providers.qwen_vllm_provider.call_qwen_vllm", _fake_call)
    provider = QwenVLLMProvider(base_url="http://127.0.0.1:8000/v1", model="Qwen/Test", timeout_seconds=7)

    result = provider.generate(_prompt(), token_budget=321, temperature=0.3)

    assert result.runtime_generation_status == "REAL_LLM"
    assert captured["base_url"] == "http://127.0.0.1:8000/v1"
    assert captured["timeout"] == 7
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "Qwen/Test"
    assert payload["max_tokens"] == 321
    assert payload["temperature"] == 0.3


def test_external_provider_fail_closed_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = ExternalProvider(provider_profile=ProviderProfile.EXTERNAL_OPENAI)
    result = provider.generate(_prompt(), token_budget=100)
    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is False
    assert "OPENAI_API_KEY" in str(result.exact_provider_error)


def test_external_provider_uses_injected_transport(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _transport(request):
        assert request["provider_profile"] == "external_openai"
        assert request["max_tokens"] == 100
        return {"text": "external output", "model": "external-test-model"}

    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model="external-test-model",
        transport=_transport,
    )
    gateway = ProviderGateway({ProviderProfile.EXTERNAL_OPENAI: provider})

    result = gateway.generate(ProviderProfile.EXTERNAL_OPENAI, _prompt(), token_budget=100)

    assert result.runtime_generation_status == "REAL_LLM"
    assert result.raw_model_output == "external output"
    assert result.provider_requested == "external_openai"


def test_external_default_routes_to_registered_external_provider(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=lambda _request: {"text": "default external"},
    )
    gateway = ProviderGateway({ProviderProfile.EXTERNAL_OPENAI: provider})
    result = gateway.generate(ProviderProfile.EXTERNAL_DEFAULT, _prompt(), token_budget=80)
    assert result.raw_model_output == "default external"
