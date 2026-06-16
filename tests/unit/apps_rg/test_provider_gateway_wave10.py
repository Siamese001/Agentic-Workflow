"""Wave 10A apps_rg provider gateway tests."""
from __future__ import annotations

import time
import json
from types import SimpleNamespace

import pytest

import apps_rg.runtime.providers.external_provider as external_provider_module
import apps_rg.runtime.providers.section_provider_call as section_provider_call_module
from apps_rg.runtime.section_model_limits import DEFAULT_EXTERNAL_CLAUDE_MODEL, external_claude_generation_model
from apps_rg.runtime.sections.section_generation import build_section_request
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
    assert profiles["external_claude_generator"]["default_model"] == DEFAULT_EXTERNAL_CLAUDE_MODEL
    assert "local_qwen_generator" not in profiles


def test_external_claude_default_model_is_sonnet() -> None:
    # Default tier is sonnet (high-signal). Haiku is applied per-section via provider_profiles.yaml
    # model_by_section (competencies + 4 narratives), NEVER as the section-agnostic default.
    assert external_claude_generation_model({}) == DEFAULT_EXTERNAL_CLAUDE_MODEL
    assert "haiku" not in DEFAULT_EXTERNAL_CLAUDE_MODEL


def test_section_request_uses_external_claude_default_model() -> None:
    request, payload = build_section_request(
        messages=[{"role": "user", "content": "Return competencies JSON."}],
        prompt_hash="prompt-hash",
        input_payload_hash="input-hash",
    )

    assert request.provider_requested == "external_claude"
    assert request.model == DEFAULT_EXTERNAL_CLAUDE_MODEL
    assert payload["model"] == DEFAULT_EXTERNAL_CLAUDE_MODEL


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

        def generate(
            self,
            compiled_prompt,
            *,
            token_budget: int,
            temperature: float = 0.7,
            timeout_seconds: int | float | None = None,
        ):
            return ProviderResult(
                provider_requested="external_claude",
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status="REAL_LLM",
                model="m",
                raw_model_output=f"{compiled_prompt.run_id}:{token_budget}:{temperature}:{timeout_seconds}",
                provider_response={},
            )

    gateway = ProviderGateway({ProviderProfile.EXTERNAL_CLAUDE: _Provider()})
    result = gateway.generate(
        ProviderProfile.EXTERNAL_CLAUDE,
        _prompt(),
        token_budget=123,
        temperature=0.2,
        timeout_seconds=12,
    )
    assert result.raw_model_output == "run-1:123:0.2:12"


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
        assert request["timeout_seconds"] == 90.0
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


def test_openai_responses_transport_omits_temperature_for_catalog_model(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"output_text": "{\"ok\":true}", "model": "gpt-catalog"}).encode("utf-8")

    def _urlopen(req, timeout):
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Response()

    monkeypatch.setattr(external_provider_module.urllib.request, "urlopen", _urlopen)
    monkeypatch.setattr(
        external_provider_module,
        "OPENAI_OMIT_TEMPERATURE_MODELS",
        frozenset({"gpt-catalog"}),
    )
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model="gpt-catalog",
        environ={"OPENAI_API_KEY": "test"},
    )

    response = provider._openai_responses_transport(
        {"prompt": "Return JSON", "max_tokens": 20, "temperature": 0.4, "timeout_seconds": 5}
    )

    assert response["text"] == "{\"ok\":true}"
    assert captured["body"]["model"] == "gpt-catalog"
    assert "temperature" not in captured["body"]


def test_section_provider_call_threads_payload_timeout_to_gateway(monkeypatch) -> None:
    calls: dict[str, object] = {}

    class _Gateway:
        def generate(
            self,
            profile,
            compiled_prompt,
            *,
            token_budget: int,
            temperature: float = 0.7,
            timeout_seconds: int | float | None = None,
        ):
            calls.update(
                {
                    "profile": profile,
                    "prompt_blocks": len(compiled_prompt.prompt_blocks),
                    "token_budget": token_budget,
                    "temperature": temperature,
                    "timeout_seconds": timeout_seconds,
                }
            )
            return ProviderResult(
                provider_requested="external_claude",
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status="REAL_LLM",
                model="m",
                raw_model_output="ok",
                provider_response={},
            )

    monkeypatch.setattr(
        section_provider_call_module,
        "build_section_provider_gateway",
        lambda: _Gateway(),
    )

    result = section_provider_call_module.call_section_model_provider(
        "external_claude",
        {
            "messages": [{"role": "user", "content": "Write one bullet."}],
            "max_tokens": 44,
            "temperature": 0.33,
            "timeout_seconds": 7,
        },
    )

    assert result.runtime_generation_status == "REAL_LLM"
    assert calls == {
        "profile": ProviderProfile.EXTERNAL_CLAUDE,
        "prompt_blocks": 1,
        "token_budget": 44,
        "temperature": 0.33,
        "timeout_seconds": 7,
    }


def test_external_provider_wall_clock_timeout_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def _slow_transport(_request):
        time.sleep(0.25)
        return {"text": "late output"}

    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=_slow_transport,
    )

    started = time.perf_counter()
    result = provider.generate(_prompt(), token_budget=100, timeout_seconds=0.01)
    elapsed = time.perf_counter() - started

    assert elapsed < 0.2
    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_attempted is True
    assert result.provider_available is False
    assert "wall-clock timeout" in str(result.exact_provider_error)


def test_external_default_routes_to_registered_external_provider(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        transport=lambda _request: {"text": "default external"},
    )
    gateway = ProviderGateway({ProviderProfile.EXTERNAL_OPENAI: provider})
    result = gateway.generate(ProviderProfile.EXTERNAL_DEFAULT, _prompt(), token_budget=80)
    assert result.raw_model_output == "default external"
