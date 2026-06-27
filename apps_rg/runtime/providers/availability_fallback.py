"""apps_rg generation-only provider availability fallback policy."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Mapping

from apps_rg.runtime.providers.external_provider import ExternalProvider
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderProfile
from apps_rg.runtime.section_model_limits import external_openai_generation_model

_HTTP_STATUS_RE = re.compile(r"\bHTTP\s+(\d{3})\b", re.IGNORECASE)
_TRANSPORT_AVAILABILITY_MARKERS = (
    "connection aborted",
    "connection refused",
    "connection reset",
    "jsondecodeerror",
    "oserror",
    "remote end closed",
    "sslerror",
    "temporarily unavailable",
    "timeout",
    "timed out",
    "urlerror",
)

_FALLBACK_ALLOWED_REASON_CATEGORIES = frozenset(
    {"provider_availability_failure", "provider_throttling_failure"}
)
_FALLBACK_FORBIDDEN_REASON_CATEGORIES = (
    "missing_evidence",
    "bad_input",
    "weak_output",
    "content_quality_failure",
    "parsing_failure",
    "validation_failure",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_status_code(error: str) -> int | None:
    match = _HTTP_STATUS_RE.search(error)
    if not match:
        return None
    return int(match.group(1))


def _availability_failure_category(result: ProviderResult) -> str | None:
    error = str(result.exact_provider_error or "")
    status_code = _http_status_code(error)
    if status_code is not None:
        if status_code == 429:
            return "provider_throttling_failure"
        if status_code == 400 and any(
            marker in error.lower()
            for marker in ("usage limit", "rate limit", "rate_limit", "quota", "credit")
        ):
            return "provider_throttling_failure"
        if status_code == 408 or 500 <= status_code <= 599:
            return "provider_availability_failure"
        return None
    lowered = error.lower()
    if "credential unavailable" in lowered:
        return None
    if any(marker in lowered for marker in _TRANSPORT_AVAILABILITY_MARKERS):
        if "rate" in lowered and "limit" in lowered:
            return "provider_throttling_failure"
        return "provider_availability_failure"
    return None


def is_claude_generation_availability_failure(result: ProviderResult) -> bool:
    """True only for Claude generation transport/API availability failures."""
    if str(result.provider_requested or "").strip().lower() != ProviderProfile.EXTERNAL_CLAUDE.value:
        return False
    if result.runtime_generation_status != "BLOCKED" or not result.provider_attempted:
        return False
    return _availability_failure_category(result) in _FALLBACK_ALLOWED_REASON_CATEGORIES


def _attempt_started_at(result: ProviderResult) -> str | None:
    response = result.provider_response if isinstance(result.provider_response, dict) else {}
    timing = response.get("transport_timing") if isinstance(response.get("transport_timing"), dict) else {}
    progress = response.get("transport_progress") if isinstance(response.get("transport_progress"), dict) else {}
    transport_response = (
        response.get("transport_response") if isinstance(response.get("transport_response"), dict) else {}
    )
    transport_timing = (
        transport_response.get("transport_timing")
        if isinstance(transport_response.get("transport_timing"), dict)
        else {}
    )
    for candidate in (
        response.get("attempt_started_at_utc"),
        timing.get("started_at"),
        progress.get("started_at"),
        transport_timing.get("started_at"),
    ):
        if str(candidate or "").strip():
            return str(candidate)
    return None


def _attempt_completed_at(result: ProviderResult) -> str | None:
    response = result.provider_response if isinstance(result.provider_response, dict) else {}
    for candidate in (response.get("attempt_completed_at_utc"),):
        if str(candidate or "").strip():
            return str(candidate)
    return None


def _fallback_receipt(
    *,
    initial_result: ProviderResult,
    fallback_result: ProviderResult | None,
    fallback_model: str,
    attempted: bool,
    reason_category: str,
    fallback_attempt_started_at_utc: str | None,
    fallback_attempt_completed_at_utc: str | None,
    receipt_created_at_utc: str | None = None,
) -> dict[str, Any]:
    fallback_provider = ProviderProfile.EXTERNAL_OPENAI.value
    fallback_runtime_status = (
        fallback_result.runtime_generation_status if fallback_result is not None else None
    )
    fallback_output_accepted = fallback_runtime_status == "REAL_LLM"
    accepted_provider = fallback_provider if fallback_output_accepted else None
    accepted_model = fallback_result.model if fallback_output_accepted and fallback_result else None
    receipt: dict[str, Any] = {
        "policy": "apps_rg_generation_claude_availability_to_openai_ssot",
        "scope": "apps_rg_generation_only",
        "receipt_created_at_utc": receipt_created_at_utc or _utc_now(),
        "fallback_allowed": reason_category in _FALLBACK_ALLOWED_REASON_CATEGORIES,
        "fallback_allowed_reason_category": reason_category,
        "fallback_forbidden_reason_categories": list(_FALLBACK_FORBIDDEN_REASON_CATEGORIES),
        "no_fallback_on_quality_content_or_validation_failure": True,
        "requested_provider": initial_result.provider_requested,
        "requested_model": initial_result.model,
        "initial_provider_requested": initial_result.provider_requested,
        "initial_model": initial_result.model,
        "initial_attempt_started_at_utc": _attempt_started_at(initial_result),
        "initial_attempt_completed_at_utc": _attempt_completed_at(initial_result),
        "initial_runtime_generation_status": initial_result.runtime_generation_status,
        "initial_exact_provider_error": initial_result.exact_provider_error,
        "fallback_provider_actual": fallback_provider,
        "fallback_model": fallback_model,
        "fallback_model_source": "apps_rg/config/provider_profiles.yaml:profiles.external_openai_generator.default_model",
        "fallback_attempted": attempted,
        "fallback_attempt_started_at_utc": fallback_attempt_started_at_utc,
        "fallback_attempt_completed_at_utc": fallback_attempt_completed_at_utc,
        "fallback_reason": reason_category,
        "fallback_output_accepted": fallback_output_accepted,
        "accepted_output_provider": accepted_provider,
        "accepted_output_model": accepted_model,
        "accepted_output_source": "fallback_provider" if fallback_output_accepted else "initial_blocked_result",
        "model_attempts": [
            {
                "attempt": "requested",
                "provider": initial_result.provider_requested,
                "model": initial_result.model,
                "started_at_utc": _attempt_started_at(initial_result),
                "completed_at_utc": _attempt_completed_at(initial_result),
                "runtime_generation_status": initial_result.runtime_generation_status,
                "exact_provider_error": initial_result.exact_provider_error,
            },
            {
                "attempt": "fallback",
                "provider": fallback_provider,
                "model": fallback_model,
                "started_at_utc": fallback_attempt_started_at_utc,
                "completed_at_utc": fallback_attempt_completed_at_utc,
                "runtime_generation_status": fallback_runtime_status,
                "exact_provider_error": (
                    fallback_result.exact_provider_error if fallback_result is not None else None
                ),
            },
        ],
    }
    if fallback_result is not None:
        receipt.update(
            {
                "fallback_runtime_generation_status": fallback_result.runtime_generation_status,
                "fallback_exact_provider_error": fallback_result.exact_provider_error,
            }
        )
    return receipt


def _with_availability_receipt(result: ProviderResult, receipt: dict[str, Any]) -> ProviderResult:
    merged_receipt = dict(result.reasoning_execution_receipt or {})
    merged_receipt["apps_rg_availability_fallback"] = receipt
    provider_response = dict(result.provider_response or {})
    provider_response["apps_rg_availability_fallback"] = receipt
    return replace(
        result,
        provider_response=provider_response or result.provider_response,
        reasoning_execution_receipt=merged_receipt,
    )


def maybe_fallback_to_openai_for_claude_availability(
    initial_result: ProviderResult,
    compiled_prompt: Any,
    *,
    token_budget: int,
    temperature: float,
    timeout_seconds: int | float | None = None,
    environ: Mapping[str, str] | None = None,
) -> ProviderResult:
    """Fallback apps_rg generation from Claude to OpenAI only for availability failures.

    This is intentionally not used by judges. It runs before any section-output parsing,
    so malformed/low-quality model content never triggers a provider substitution.
    """
    if not is_claude_generation_availability_failure(initial_result):
        return initial_result

    reason_category = _availability_failure_category(initial_result)
    if reason_category not in _FALLBACK_ALLOWED_REASON_CATEGORIES:
        return initial_result

    fallback_model = external_openai_generation_model()
    fallback_provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model=fallback_model,
        environ=environ,
    )
    fallback_attempt_started_at_utc = _utc_now()
    fallback_result = fallback_provider.generate(
        compiled_prompt,
        token_budget=token_budget,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    fallback_attempt_completed_at_utc = _utc_now()
    receipt = _fallback_receipt(
        initial_result=initial_result,
        fallback_result=fallback_result,
        fallback_model=fallback_model,
        attempted=fallback_result.provider_attempted,
        reason_category=reason_category,
        fallback_attempt_started_at_utc=fallback_attempt_started_at_utc,
        fallback_attempt_completed_at_utc=fallback_attempt_completed_at_utc,
    )
    if fallback_result.runtime_generation_status == "REAL_LLM":
        return _with_availability_receipt(
            replace(fallback_result, provider_requested=initial_result.provider_requested),
            receipt,
        )
    return _with_availability_receipt(initial_result, receipt)


__all__ = [
    "is_claude_generation_availability_failure",
    "maybe_fallback_to_openai_for_claude_availability",
]
