from __future__ import annotations

import apps_rg.runtime.providers.section_provider_call as section_provider_call
from apps_rg.runtime.providers import anthropic_prompt_cache as subject
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderProfile
from apps_rg.runtime.sections.section_generation import build_section_request


class _CapturingGateway:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        profile,
        compiled_prompt,
        *,
        token_budget: int,
        temperature: float = 0.7,
        timeout_seconds: int | float | None = None,
    ) -> ProviderResult:
        self.calls.append(
            {
                "profile": profile,
                "compiled_prompt": compiled_prompt,
                "token_budget": token_budget,
                "temperature": temperature,
                "timeout_seconds": timeout_seconds,
            }
        )
        return ProviderResult(
            provider_requested=str(getattr(profile, "value", profile)),
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="test-model",
            raw_model_output="ok",
            provider_response={"captured": True},
        )


def test_prompt_cache_flags_default_off_and_enable_only_on_one() -> None:
    env: dict[str, str] = {}

    assert subject.anthropic_prompt_cache_enabled(env) is False
    assert subject.anthropic_prompt_cache_telemetry_enabled(env) is False
    assert subject.anthropic_prompt_cache_prewarm_enabled(env) is False
    assert subject.anthropic_prompt_cache_fanout_enabled(env) is False

    env = {
        subject.ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE: "1",
        subject.ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY: "true",
        subject.ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM: "0",
        subject.ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT: "",
    }

    assert subject.anthropic_prompt_cache_enabled(env) is True
    assert subject.anthropic_prompt_cache_telemetry_enabled(env) is False
    assert subject.anthropic_prompt_cache_prewarm_enabled(env) is False
    assert subject.anthropic_prompt_cache_fanout_enabled(env) is False


def test_disabled_cache_receipt_has_provider_neutral_schema() -> None:
    receipt = subject.build_disabled_cache_receipt(
        provider="external_claude",
        model="claude-sonnet-5",
        section_id="competencies",
    )

    assert receipt == {
        "provider": "external_claude",
        "model": "claude-sonnet-5",
        "section_id": "competencies",
        "cache_enabled": False,
        "cache_strategy": "disabled",
        "stable_prefix_hash": "",
        "c0_prefix_hash": "",
        "volatile_tail_hash": "",
        "cache_marker_count": 0,
        "input_tokens": None,
        "output_tokens": None,
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "cache_hit_ratio": None,
        "estimated_uncached_input_tokens": None,
        "estimated_cached_input_tokens": None,
        "cache_savings_estimate_source": "not_estimated_cache_disabled",
    }


def test_cache_flag_off_preserves_section_payload_shape() -> None:
    _request, payload = build_section_request(
        messages=[{"role": "user", "content": "Write JSON."}],
        prompt_hash="prompt-hash",
        input_payload_hash="input-hash",
        model="claude-sonnet-5",
    )

    assert payload == {
        "model": "claude-sonnet-5",
        "messages": [{"role": "user", "content": "Write JSON."}],
        "temperature": 0.45,
        "max_tokens": 700,
        "timeout_seconds": 90,
        "response_format": {"type": "json_object"},
    }
    assert "cache_control" not in str(payload)


def test_section_provider_emits_disabled_receipt_without_changing_runtime_status(
    monkeypatch,
    tmp_path,
) -> None:
    gateway = _CapturingGateway()
    monkeypatch.setattr(
        section_provider_call,
        "build_section_provider_gateway",
        lambda claude_model=None, openai_model=None: gateway,
    )

    result = section_provider_call.call_section_model_provider(
        ProviderProfile.EXTERNAL_CLAUDE,
        {
            "messages": [{"role": "user", "content": "Write one bullet."}],
            "prompt_hash": "prompt-hash",
            "request_id": "request-1",
            "run_id": "payload-run",
            "max_tokens": 44,
            "temperature": 0.42,
            "timeout_seconds": 7,
        },
        artifact_dir=tmp_path,
        run_id="explicit-run",
        section_id="competencies",
    )

    assert result.runtime_generation_status == "REAL_LLM"
    assert result.exact_provider_error is None
    assert result.prompt_cache_receipt is not None
    assert result.prompt_cache_receipt["cache_enabled"] is False
    assert result.prompt_cache_receipt["cache_marker_count"] == 0
    assert result.provider_response is not None
    assert result.provider_response["captured"] is True
    assert result.provider_response["provider_cache_receipt"] == result.prompt_cache_receipt
    assert not any(tmp_path.iterdir())

    call = gateway.calls[0]
    compiled = call["compiled_prompt"]
    assert [(b.role, b.content) for b in compiled.prompt_blocks] == [
        ("user", "Write one bullet."),
    ]
