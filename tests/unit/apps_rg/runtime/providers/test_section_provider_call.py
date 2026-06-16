from __future__ import annotations

import apps_rg.runtime.providers.section_provider_call as subject
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderProfile


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


def test_build_section_provider_gateway_registers_external_profiles() -> None:
    gateway = subject.build_section_provider_gateway()

    assert set(gateway.registered_profiles()) == {
        ProviderProfile.EXTERNAL_CLAUDE,
        ProviderProfile.EXTERNAL_OPENAI,
    }


def test_call_section_model_provider_threads_messages_and_overrides(monkeypatch) -> None:
    gateway = _CapturingGateway()
    monkeypatch.setattr(subject, "build_section_provider_gateway", lambda: gateway)

    result = subject.call_section_model_provider(
        "claude",
        {
            "messages": [
                {"role": "system", "content": "System guard."},
                {"role": "user", "content": "Write one bullet."},
                {"role": "assistant", "content": ""},
                "invalid",
            ],
            "prompt_hash": "prompt-hash",
            "request_id": "request-1",
            "run_id": "payload-run",
            "max_tokens": 44,
            "temperature": 0.91,
            "timeout_seconds": 7,
        },
        run_id="explicit-run",
        temperature_override=0.33,
    )

    assert result.runtime_generation_status == "REAL_LLM"
    call = gateway.calls[0]
    compiled = call["compiled_prompt"]
    assert call["profile"] == ProviderProfile.EXTERNAL_CLAUDE
    assert call["token_budget"] == 44
    assert call["temperature"] == 0.33
    assert call["timeout_seconds"] == 7
    assert compiled.compilation_hash == "prompt-hash"
    assert compiled.request_id == "request-1"
    assert compiled.run_id == "explicit-run"
    assert [(b.role, b.content) for b in compiled.prompt_blocks] == [
        ("system", "System guard."),
        ("user", "Write one bullet."),
    ]


def test_call_section_model_provider_falls_back_to_prompt_and_max_output_tokens(
    monkeypatch,
) -> None:
    gateway = _CapturingGateway()
    monkeypatch.setattr(subject, "build_section_provider_gateway", lambda: gateway)

    subject.call_section_model_provider(
        ProviderProfile.EXTERNAL_OPENAI,
        {
            "messages": [{"role": "user", "content": ""}],
            "prompt": "Fallback prompt body.",
            "run_id": "payload-run",
            "max_output_tokens": 123,
        },
    )

    call = gateway.calls[0]
    compiled = call["compiled_prompt"]
    assert call["profile"] == ProviderProfile.EXTERNAL_OPENAI
    assert call["token_budget"] == 123
    assert call["temperature"] == 0.45
    assert call["timeout_seconds"] is None
    assert compiled.run_id == "payload-run"
    assert [(b.role, b.content) for b in compiled.prompt_blocks] == [
        ("user", "Fallback prompt body."),
    ]


def test_call_section_model_provider_explicit_token_budget_wins(monkeypatch) -> None:
    gateway = _CapturingGateway()
    monkeypatch.setattr(subject, "build_section_provider_gateway", lambda: gateway)

    subject.call_section_model_provider(
        None,
        {
            "prompt": "Use defaults.",
            "max_tokens": 10,
            "max_output_tokens": 20,
        },
        token_budget=77,
    )

    call = gateway.calls[0]
    assert call["profile"] == ProviderProfile.EXTERNAL_CLAUDE
    assert call["token_budget"] == 77

