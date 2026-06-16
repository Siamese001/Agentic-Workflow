from __future__ import annotations

from types import SimpleNamespace

from apps_rg.runtime.providers import availability_fallback as subject
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderProfile


def _result(
    *,
    provider_requested: str = "external_claude",
    attempted: bool = True,
    status: str = "BLOCKED",
    error: str | None = "External provider HTTP 429: rate_limit_error",
    raw: str = "",
) -> ProviderResult:
    return ProviderResult(
        provider_requested=provider_requested,
        provider_attempted=attempted,
        provider_available=status == "REAL_LLM",
        exact_provider_error=error,
        runtime_generation_status=status,
        model="claude-sonnet-4-6",
        raw_model_output=raw,
        provider_response=None,
    )


def test_claude_rate_limit_is_availability_failure() -> None:
    assert subject.is_claude_generation_availability_failure(
        _result(error="External provider HTTP 429: rate_limit_error")
    )


def test_claude_transport_timeout_is_availability_failure() -> None:
    assert subject.is_claude_generation_availability_failure(
        _result(error="External provider call failed: TimeoutError: timed out")
    )


def test_http_400_content_or_request_issue_does_not_fallback() -> None:
    assert not subject.is_claude_generation_availability_failure(
        _result(error="External provider HTTP 400: invalid_request_error")
    )


def test_successful_bad_content_does_not_fallback() -> None:
    initial = _result(status="REAL_LLM", error=None, raw="not json")
    assert subject.maybe_fallback_to_openai_for_claude_availability(
        initial,
        SimpleNamespace(run_id="run"),
        token_budget=100,
        temperature=0.2,
    ) is initial


def test_openai_fallback_uses_ssot_model_and_preserves_initial_provider_request(monkeypatch) -> None:
    created: dict[str, object] = {}

    class _FallbackProvider:
        def __init__(self, *, provider_profile, model, environ=None) -> None:
            created["provider_profile"] = provider_profile
            created["model"] = model

        def generate(self, compiled_prompt, *, token_budget, temperature=0.7, timeout_seconds=None):
            created["token_budget"] = token_budget
            created["temperature"] = temperature
            created["timeout_seconds"] = timeout_seconds
            return ProviderResult(
                provider_requested=ProviderProfile.EXTERNAL_OPENAI.value,
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status="REAL_LLM",
                model=str(created["model"]),
                raw_model_output='{"ok": true}',
                provider_response={"provider_profile": ProviderProfile.EXTERNAL_OPENAI.value},
            )

    monkeypatch.setattr(subject, "ExternalProvider", _FallbackProvider)
    monkeypatch.setattr(subject, "external_openai_generation_model_from_ssot", lambda: "gpt-ssot")

    initial = _result(error="External provider HTTP 529: overloaded_error")
    result = subject.maybe_fallback_to_openai_for_claude_availability(
        initial,
        SimpleNamespace(run_id="run"),
        token_budget=321,
        temperature=0.11,
        timeout_seconds=9,
    )

    assert created["provider_profile"] == ProviderProfile.EXTERNAL_OPENAI
    assert created["model"] == "gpt-ssot"
    assert created["token_budget"] == 321
    assert created["temperature"] == 0.11
    assert created["timeout_seconds"] == 9
    assert result.runtime_generation_status == "REAL_LLM"
    assert result.provider_requested == ProviderProfile.EXTERNAL_CLAUDE.value
    assert result.model == "gpt-ssot"
    receipt = result.reasoning_execution_receipt["apps_rg_availability_fallback"]
    assert receipt["scope"] == "apps_rg_generation_only"
    assert receipt["fallback_provider_actual"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert receipt["fallback_model"] == "gpt-ssot"


def test_openai_fallback_failure_returns_initial_blocked_result_with_receipt(monkeypatch) -> None:
    class _BlockedFallbackProvider:
        def __init__(self, *, provider_profile, model, environ=None) -> None:
            self.model = model

        def generate(self, compiled_prompt, *, token_budget, temperature=0.7, timeout_seconds=None):
            return ProviderResult(
                provider_requested=ProviderProfile.EXTERNAL_OPENAI.value,
                provider_attempted=False,
                provider_available=False,
                exact_provider_error="External provider credential unavailable: OPENAI_API_KEY",
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=None,
            )

    monkeypatch.setattr(subject, "ExternalProvider", _BlockedFallbackProvider)
    monkeypatch.setattr(subject, "external_openai_generation_model_from_ssot", lambda: "gpt-ssot")

    initial = _result(error="External provider HTTP 503: unavailable")
    result = subject.maybe_fallback_to_openai_for_claude_availability(
        initial,
        SimpleNamespace(run_id="run"),
        token_budget=100,
        temperature=0.2,
    )

    assert result.provider_requested == ProviderProfile.EXTERNAL_CLAUDE.value
    assert result.runtime_generation_status == "BLOCKED"
    assert result.exact_provider_error == initial.exact_provider_error
    receipt = result.reasoning_execution_receipt["apps_rg_availability_fallback"]
    assert receipt["fallback_attempted"] is False
    assert receipt["fallback_runtime_generation_status"] == "BLOCKED"
