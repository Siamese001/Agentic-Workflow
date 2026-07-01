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
    started_at: str = "2026-06-20T16:00:00+00:00",
    completed_at: str = "2026-06-20T16:00:01+00:00",
) -> ProviderResult:
    return ProviderResult(
        provider_requested=provider_requested,
        provider_attempted=attempted,
        provider_available=status == "REAL_LLM",
        exact_provider_error=error,
        runtime_generation_status=status,
        model="claude-sonnet-4-6",
        raw_model_output=raw,
        provider_response={
            "attempt_started_at_utc": started_at,
            "attempt_completed_at_utc": completed_at,
        },
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


def test_anthropic_http_400_deprecated_temperature_falls_back_as_capability_drift() -> None:
    assert subject.is_claude_generation_availability_failure(
        _result(
            error=(
                'External provider HTTP 400: {"type":"error","error":'
                '{"type":"invalid_request_error","message":"`temperature` is deprecated for this model."}}'
            )
        )
    )


def test_anthropic_http_400_usage_limit_falls_back_as_throttling() -> None:
    assert subject.is_claude_generation_availability_failure(
        _result(error="External provider HTTP 400: usage limit exceeded")
    )


def test_successful_bad_content_does_not_fallback() -> None:
    initial = _result(status="REAL_LLM", error=None, raw="not json")
    assert subject.maybe_fallback_to_openai_for_claude_availability(
        initial,
        SimpleNamespace(run_id="run"),
        token_budget=100,
        temperature=0.2,
    ) is initial


def test_parse_or_validation_failure_wording_does_not_fallback() -> None:
    for error in (
        "section parse failure: missing JSON",
        "X2 validation failed: weak output",
        "content quality failure: empty bullets",
        "missing evidence packet",
        "bad input: required graph packet absent",
    ):
        initial = _result(status="BLOCKED", error=error)
        assert not subject.is_claude_generation_availability_failure(initial)
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
    monkeypatch.setattr(subject, "external_openai_generation_model", lambda section_id=None: "gpt-ssot")
    monkeypatch.setattr(
        subject,
        "external_openai_generation_model_source",
        lambda section_id=None: f"source:{section_id or 'default'}",
    )

    initial = _result(error="External provider HTTP 429: rate_limit_error")
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
    assert receipt["fallback_allowed"] is True
    assert receipt["fallback_allowed_reason_category"] == "provider_throttling_failure"
    assert receipt["no_fallback_on_quality_content_or_validation_failure"] is True
    assert "parsing_failure" in receipt["fallback_forbidden_reason_categories"]
    assert receipt["requested_provider"] == ProviderProfile.EXTERNAL_CLAUDE.value
    assert receipt["requested_model"] == "claude-sonnet-4-6"
    assert receipt["initial_attempt_started_at_utc"] == "2026-06-20T16:00:00+00:00"
    assert receipt["initial_attempt_completed_at_utc"] == "2026-06-20T16:00:01+00:00"
    assert receipt["fallback_provider_actual"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert receipt["fallback_model"] == "gpt-ssot"
    assert receipt["fallback_model_source"] == "source:default"
    assert receipt["fallback_section_id"] is None
    assert receipt["fallback_attempt_started_at_utc"]
    assert receipt["fallback_attempt_completed_at_utc"]
    assert receipt["fallback_output_accepted"] is True
    assert receipt["accepted_output_provider"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert receipt["accepted_output_model"] == "gpt-ssot"
    attempts = receipt["model_attempts"]
    assert attempts[0]["provider"] == ProviderProfile.EXTERNAL_CLAUDE.value
    assert attempts[0]["model"] == "claude-sonnet-4-6"
    assert attempts[0]["started_at_utc"] == "2026-06-20T16:00:00+00:00"
    assert attempts[1]["provider"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert attempts[1]["model"] == "gpt-ssot"
    assert attempts[1]["started_at_utc"]
    spans = receipt["provider_attempt_spans"]
    assert [span["attempt_kind"] for span in spans] == ["requested", "fallback"]
    assert spans[0]["provider"] == ProviderProfile.EXTERNAL_CLAUDE.value
    assert spans[0]["duration_seconds"] == 1.0
    assert spans[0]["output_accepted"] is False
    assert spans[1]["provider"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert spans[1]["model"] == "gpt-ssot"
    assert spans[1]["fallback_reason"] == "provider_throttling_failure"
    assert spans[1]["output_accepted"] is True
    assert receipt["provider_attempt_timing_summary"]["fallback_attempt_count"] == 1
    assert result.provider_response["provider_attempt_spans"] == spans


def test_policy_locked_sections_do_not_accept_openai_generation_fallback(monkeypatch) -> None:
    created: dict[str, object] = {}

    class _FallbackProvider:
        def __init__(self, *, provider_profile, model, environ=None) -> None:
            created["provider_profile"] = provider_profile
            created["model"] = model

        def generate(self, compiled_prompt, *, token_budget, temperature=0.7, timeout_seconds=None):
            raise AssertionError("fallback provider must not be called")

    monkeypatch.setattr(subject, "ExternalProvider", _FallbackProvider)

    for section_id in ("executive_summary", "headline", "competencies"):
        initial = _result(error="External provider HTTP 429: rate_limit_error")
        assert subject.maybe_fallback_to_openai_for_claude_availability(
            initial,
            SimpleNamespace(run_id="run"),
            token_budget=321,
            temperature=0.11,
            timeout_seconds=9,
            section_id=section_id,
        ) is initial

    assert created == {}


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
    monkeypatch.setattr(subject, "external_openai_generation_model", lambda section_id=None: "gpt-ssot")

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
    assert receipt["fallback_output_accepted"] is False
    assert receipt["accepted_output_provider"] is None
    assert receipt["accepted_output_model"] is None
    assert receipt["accepted_output_source"] == "initial_blocked_result"
    spans = receipt["provider_attempt_spans"]
    assert [span["attempt_kind"] for span in spans] == ["requested", "fallback"]
    assert spans[1]["provider"] == ProviderProfile.EXTERNAL_OPENAI.value
    assert spans[1]["provider_attempted"] is False
    assert spans[1]["runtime_generation_status"] == "BLOCKED"
    assert spans[1]["output_accepted"] is False
