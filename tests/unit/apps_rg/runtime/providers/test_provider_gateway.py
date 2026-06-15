from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import (
    ENV_APPS_RG_PROVIDER_PROFILE,
    ProviderGateway,
    ProviderGatewayError,
    ProviderProfile,
    ProviderProfileNotRegisteredError,
    load_provider_profiles_config,
    normalize_provider_profile,
    resolve_provider_profile,
)


class _Provider:
    provider_profile = ProviderProfile.EXTERNAL_CLAUDE

    def __init__(self, label: str) -> None:
        self.label = label
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        compiled_prompt,
        *,
        token_budget: int,
        temperature: float = 0.7,
        timeout_seconds: int | float | None = None,
    ) -> ProviderResult:
        self.calls.append(
            {
                "prompt": compiled_prompt,
                "token_budget": token_budget,
                "temperature": temperature,
                "timeout_seconds": timeout_seconds,
            }
        )
        return ProviderResult(
            provider_requested=self.label,
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="test-model",
            raw_model_output=f"{self.label}:{token_budget}:{temperature}:{timeout_seconds}",
            provider_response={},
        )


def test_normalize_provider_profile_aliases_and_errors() -> None:
    assert normalize_provider_profile(None) == ProviderProfile.EXTERNAL_CLAUDE
    assert normalize_provider_profile("claude") == ProviderProfile.EXTERNAL_CLAUDE
    assert normalize_provider_profile("openai") == ProviderProfile.EXTERNAL_OPENAI
    assert normalize_provider_profile("external_default") == ProviderProfile.EXTERNAL_DEFAULT

    with pytest.raises(ProviderGatewayError, match="Unknown apps_rg provider profile"):
        normalize_provider_profile("local_qwen")


def test_resolve_provider_profile_precedence(monkeypatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_PROVIDER_PROFILE, "external_openai")

    explicit = resolve_provider_profile("external_claude")
    from_env = resolve_provider_profile(environ={ENV_APPS_RG_PROVIDER_PROFILE: "external_openai"})
    default = resolve_provider_profile(environ={})

    assert explicit.profile == ProviderProfile.EXTERNAL_CLAUDE
    assert explicit.source == "explicit"
    assert from_env.profile == ProviderProfile.EXTERNAL_OPENAI
    assert from_env.source == ENV_APPS_RG_PROVIDER_PROFILE
    assert default.profile == ProviderProfile.EXTERNAL_CLAUDE
    assert default.source == "apps_rg_default_external_claude"


def test_provider_gateway_routes_external_default_to_openai_then_claude() -> None:
    openai_provider = _Provider("openai")
    claude_provider = _Provider("claude")
    prompt = SimpleNamespace(run_id="run-wave2")

    result_openai = ProviderGateway(
        {
            ProviderProfile.EXTERNAL_OPENAI: openai_provider,
            ProviderProfile.EXTERNAL_CLAUDE: claude_provider,
        }
    ).generate(ProviderProfile.EXTERNAL_DEFAULT, prompt, token_budget=42, temperature=0.1)
    result_claude = ProviderGateway(
        {ProviderProfile.EXTERNAL_CLAUDE: claude_provider}
    ).generate("external_default", prompt, token_budget=43, timeout_seconds=5)

    assert result_openai.provider_requested == "openai"
    assert result_openai.raw_model_output == "openai:42:0.1:None"
    assert result_claude.provider_requested == "claude"
    assert result_claude.raw_model_output == "claude:43:0.7:5"


def test_provider_gateway_blocks_unregistered_profile() -> None:
    with pytest.raises(ProviderProfileNotRegisteredError, match="Provider not registered"):
        ProviderGateway().generate("external_openai", SimpleNamespace(), token_budget=1)


def test_load_provider_profiles_config_validates_yaml_shape(tmp_path) -> None:
    missing = tmp_path / "missing.yaml"
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("profiles:\n- not-a-map\n", encoding="utf-8")

    with pytest.raises(ProviderGatewayError, match="Missing apps_rg provider profile config"):
        load_provider_profiles_config(missing)
    with pytest.raises(ProviderGatewayError, match="missing profiles"):
        load_provider_profiles_config(invalid)
