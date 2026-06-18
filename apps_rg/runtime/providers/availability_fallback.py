"""apps_rg generation-only provider availability fallback policy."""

from __future__ import annotations

import re
from dataclasses import replace
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


def _http_status_code(error: str) -> int | None:
    match = _HTTP_STATUS_RE.search(error)
    if not match:
        return None
    return int(match.group(1))


def is_claude_generation_availability_failure(result: ProviderResult) -> bool:
    """True only for Claude generation transport/API availability failures."""
    if str(result.provider_requested or "").strip().lower() != ProviderProfile.EXTERNAL_CLAUDE.value:
        return False
    if result.runtime_generation_status != "BLOCKED" or not result.provider_attempted:
        return False
    error = str(result.exact_provider_error or "")
    if not error:
        return False
    status_code = _http_status_code(error)
    if status_code is not None:
        return status_code == 408 or status_code == 429 or 500 <= status_code <= 599
    lowered = error.lower()
    if "credential unavailable" in lowered:
        return False
    return any(marker in lowered for marker in _TRANSPORT_AVAILABILITY_MARKERS)


def _fallback_receipt(
    *,
    initial_result: ProviderResult,
    fallback_result: ProviderResult | None,
    fallback_model: str,
    attempted: bool,
    reason: str,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "policy": "apps_rg_generation_claude_availability_to_openai_ssot",
        "scope": "apps_rg_generation_only",
        "initial_provider_requested": initial_result.provider_requested,
        "initial_model": initial_result.model,
        "initial_runtime_generation_status": initial_result.runtime_generation_status,
        "initial_exact_provider_error": initial_result.exact_provider_error,
        "fallback_provider_actual": ProviderProfile.EXTERNAL_OPENAI.value,
        "fallback_model": fallback_model,
        "fallback_model_source": "apps_rg/config/provider_profiles.yaml:profiles.external_openai_generator.default_model",
        "fallback_attempted": attempted,
        "fallback_reason": reason,
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

    fallback_model = external_openai_generation_model()
    fallback_provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model=fallback_model,
        environ=environ,
    )
    fallback_result = fallback_provider.generate(
        compiled_prompt,
        token_budget=token_budget,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    receipt = _fallback_receipt(
        initial_result=initial_result,
        fallback_result=fallback_result,
        fallback_model=fallback_model,
        attempted=fallback_result.provider_attempted,
        reason="claude_availability_failure",
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
