from __future__ import annotations

from types import SimpleNamespace

from apps_rg.runtime.providers import availability_fallback as subject
from apps_rg.runtime.providers.provider_contract import ProviderResult


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
        model="claude-sonnet-5",
        raw_model_output=raw,
        provider_response={
            "attempt_started_at_utc": "2026-06-20T16:00:00+00:00",
            "attempt_completed_at_utc": "2026-06-20T16:00:01+00:00",
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


def test_anthropic_http_400_deprecated_temperature_is_capability_failure() -> None:
    assert subject.is_claude_generation_availability_failure(
        _result(
            error=(
                'External provider HTTP 400: {"type":"error","error":'
                '{"type":"invalid_request_error","message":"`temperature` is deprecated for this model."}}'
            )
        )
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


def test_claude_availability_failure_without_section_does_not_call_openai(monkeypatch) -> None:
    def _forbidden_provider(*_args, **_kwargs):
        raise AssertionError("OpenAI fallback provider must not be constructed")

    monkeypatch.setattr(subject, "ExternalProvider", _forbidden_provider)
    initial = _result(error="External provider HTTP 429: rate_limit_error")

    assert subject.maybe_fallback_to_openai_for_claude_availability(
        initial,
        SimpleNamespace(run_id="run"),
        token_budget=321,
        temperature=0.11,
        timeout_seconds=9,
    ) is initial


def test_policy_locked_sections_do_not_call_openai_fallback(monkeypatch) -> None:
    def _forbidden_provider(*_args, **_kwargs):
        raise AssertionError("OpenAI fallback provider must not be constructed")

    monkeypatch.setattr(subject, "ExternalProvider", _forbidden_provider)

    for section_id in (
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
        "executive_summary",
        "headline",
    ):
        initial = _result(error="External provider HTTP 429: rate_limit_error")
        assert subject.maybe_fallback_to_openai_for_claude_availability(
            initial,
            SimpleNamespace(run_id="run"),
            token_budget=321,
            temperature=0.11,
            timeout_seconds=9,
            section_id=section_id,
        ) is initial
