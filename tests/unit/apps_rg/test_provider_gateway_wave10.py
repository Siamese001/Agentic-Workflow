"""Wave 10A apps_rg provider gateway tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import apps_rg.runtime.providers.external_provider as external_provider_module
from apps_rg.runtime.providers import (
    ExternalProvider,
    ProviderGateway,
    ProviderProfile,
    ProviderProfileNotRegisteredError,
    load_provider_profiles_config,
    resolve_provider_profile,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult


def _prompt() -> SimpleNamespace:
    return SimpleNamespace(
        request_id="req-1",
        run_id="run-1",
        compilation_hash="abc123",
        prompt_blocks=(),
        system_preamble="System",
        user_instruction="Write a concise resume section.",
    )


def test_provider_profiles_config_uses_external_claude_default() -> None:
    data = load_provider_profiles_config()
    assert data["wave10a_policy"]["default_provider"] == "external_claude"
    assert data["wave10a_policy"]["external_default_status"] == "claude_default_for_apps_rg_e2e"
    profiles = data["profiles"]
    assert profiles["external_openai_generator"]["default"] is False
    assert profiles["external_claude_generator"]["default"] is True
    assert "local_qwen_generator" not in profiles


def test_provider_profile_resolution_defaults_to_external_claude(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_PROVIDER_PROFILE", raising=False)
    selected = resolve_provider_profile()
    assert selected.profile == ProviderProfile.EXTERNAL_CLAUDE
    assert selected.source == "apps_rg_default_external_claude"


def test_wave10a_provider_profile_env_selects_external(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_PROVIDER_PROFILE", "external_openai")
    selected = resolve_provider_profile()
    assert selected.profile == ProviderProfile.EXTERNAL_OPENAI
    assert selected.source == "APPS_RG_PROVIDER_PROFILE"


def test_provider_gateway_dispatches_registered_provider() -> None:
    class _Provider:
        provider_profile = ProviderProfile.EXTERNAL_CLAUDE

        def generate(self, compiled_prompt, *, token_budget: int, temperature: float = 0.7):
            return ProviderResult(
                provider_requested="external_claude",
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status="REAL_LLM",
                model="m",
                raw_model_output=f"{compiled_prompt.run_id}:{token_budget}:{temperature}",
                provider_response={},
            )

    gateway = ProviderGateway({ProviderProfile.EXTERNAL_CLAUDE: _Provider()})
    result = gateway.generate(ProviderProfile.EXTERNAL_CLAUDE, _prompt(), token_budget=123, temperature=0.2)
    assert result.raw_model_output == "run-1:123:0.2"


def test_provider_gateway_blocks_unregistered_profile() -> None:
    gateway = ProviderGateway()
    with pytest.raises(ProviderProfileNotRegisteredError):
        gateway.generate(ProviderProfile.EXTERNAL_OPENAI, _prompt(), token_budget=10)


def test_external_provider_fail_closed_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = ExternalProvider(provider_profile=ProviderProfile.EXTERNAL_OPENAI, environ={})
    result = provider.generate(_prompt(), token_budget=100)
    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is False
    assert "OPENAI_API_KEY" in str(result.exact_provider_error)


def test_external_provider_bootstraps_process_env_before_credential_gate(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    calls = {"count": 0}

    def _bootstrap(environ) -> None:
        calls["count"] += 1
        monkeypatch.setenv("OPENAI_API_KEY", "dotenv-openai")

    monkeypatch.setattr(
        external_provider_module,
        "bootstrap_process_env_if_needed",
        _bootstrap,
    )
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=lambda _request: {"text": "bootstrapped output"},
    )

    result = provider.generate(_prompt(), token_budget=100)

    assert calls["count"] == 1
    assert result.runtime_generation_status == "REAL_LLM"
    assert result.raw_model_output == "bootstrapped output"


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
