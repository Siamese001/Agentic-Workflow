"""Normalized apps_rg provider attempt span receipts.

These spans are receipt data, not provider routing. They make provider timing
and fallback timing readable without reconstructing several artifacts.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping

SPAN_SCHEMA_VERSION = "apps_rg_provider_attempt_span_v1"
TIMING_SUMMARY_SCHEMA_VERSION = "apps_rg_provider_attempt_timing_summary_v1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def duration_seconds(started_at_utc: Any, completed_at_utc: Any) -> float | None:
    start = _parse_iso(started_at_utc)
    end = _parse_iso(completed_at_utc)
    if start is None or end is None:
        return None
    return round(max((end - start).total_seconds(), 0.0), 6)


def _clean_mapping(value: Any, *, allowed_keys: tuple[str, ...]) -> dict[str, Any] | None:
    if not isinstance(value, Mapping):
        return None
    out: dict[str, Any] = {}
    for key in allowed_keys:
        if key in value:
            out[key] = deepcopy(value[key])
    return out or None


def compact_transport_progress(value: Any) -> dict[str, Any] | None:
    return _clean_mapping(
        value,
        allowed_keys=(
            "started_at",
            "first_byte_after_s",
            "last_progress_after_s",
            "completed_after_s",
            "chunk_count",
            "raw_output_chars",
            "completed",
        ),
    )


def compact_transport_timing(value: Any) -> dict[str, Any] | None:
    return _clean_mapping(
        value,
        allowed_keys=(
            "started_at",
            "first_byte_after_s",
            "last_progress_after_s",
            "completed_after_s",
            "chunk_count",
            "read_iterations",
            "raw_output_chars",
            "stream",
        ),
    )


def build_provider_attempt_span(
    *,
    attempt_kind: str,
    attempt_index: int,
    provider: str,
    model: str,
    provider_attempted: bool,
    provider_available: bool,
    runtime_generation_status: str,
    started_at_utc: str | None,
    completed_at_utc: str | None,
    exact_provider_error: str | None = None,
    timeout_seconds: Any | None = None,
    token_budget: Any | None = None,
    temperature: Any | None = None,
    request_digest: str | None = None,
    section_id: str | None = None,
    fallback_reason: str | None = None,
    output_accepted: bool | None = None,
    accepted_output_source: str | None = None,
    transport_progress: Mapping[str, Any] | None = None,
    transport_timing: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    span: dict[str, Any] = {
        "schema_version": SPAN_SCHEMA_VERSION,
        "span_kind": "provider_attempt",
        "attempt_kind": str(attempt_kind or "requested"),
        "attempt_index": int(attempt_index),
        "provider": str(provider or ""),
        "model": str(model or ""),
        "provider_attempted": bool(provider_attempted),
        "provider_available": bool(provider_available),
        "runtime_generation_status": str(runtime_generation_status or ""),
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "duration_seconds": duration_seconds(started_at_utc, completed_at_utc),
        "exact_provider_error": exact_provider_error,
        "timeout_seconds": timeout_seconds,
        "token_budget": token_budget,
        "temperature": temperature,
    }
    if request_digest:
        span["request_digest"] = str(request_digest)
    if section_id:
        span["section_id"] = str(section_id)
    if fallback_reason:
        span["fallback_reason"] = str(fallback_reason)
    if output_accepted is not None:
        span["output_accepted"] = bool(output_accepted)
    if accepted_output_source:
        span["accepted_output_source"] = str(accepted_output_source)
    progress = compact_transport_progress(transport_progress)
    if progress is not None:
        span["transport_progress"] = progress
    timing = compact_transport_timing(transport_timing)
    if timing is not None:
        span["transport_timing"] = timing
    return span


def _response_mapping_from_result(result: Any) -> Mapping[str, Any]:
    response = getattr(result, "provider_response", None)
    return response if isinstance(response, Mapping) else {}


def _first_existing_span(result: Any) -> dict[str, Any] | None:
    response = _response_mapping_from_result(result)
    spans = response.get("provider_attempt_spans")
    if isinstance(spans, list):
        for span in spans:
            if isinstance(span, Mapping):
                return dict(span)
    return None


def _started_at_from_response(response: Mapping[str, Any]) -> str | None:
    transport_timing = response.get("transport_timing")
    progress = response.get("transport_progress")
    transport_response = response.get("transport_response")
    nested_timing = (
        transport_response.get("transport_timing")
        if isinstance(transport_response, Mapping)
        else None
    )
    for candidate in (
        response.get("attempt_started_at_utc"),
        transport_timing.get("started_at") if isinstance(transport_timing, Mapping) else None,
        progress.get("started_at") if isinstance(progress, Mapping) else None,
        nested_timing.get("started_at") if isinstance(nested_timing, Mapping) else None,
    ):
        if str(candidate or "").strip():
            return str(candidate)
    return None


def _completed_at_from_response(response: Mapping[str, Any]) -> str | None:
    for candidate in (response.get("attempt_completed_at_utc"),):
        if str(candidate or "").strip():
            return str(candidate)
    return None


def provider_result_attempt_span(
    result: Any,
    *,
    attempt_kind: str,
    attempt_index: int,
    section_id: str | None = None,
    fallback_reason: str | None = None,
    output_accepted: bool | None = None,
    accepted_output_source: str | None = None,
    fallback_started_at_utc: str | None = None,
    fallback_completed_at_utc: str | None = None,
) -> dict[str, Any]:
    existing = _first_existing_span(result)
    if existing is not None:
        span = dict(existing)
        span.setdefault("schema_version", SPAN_SCHEMA_VERSION)
        span.setdefault("span_kind", "provider_attempt")
        span["attempt_kind"] = attempt_kind
        span["attempt_index"] = attempt_index
        if section_id:
            span["section_id"] = section_id
        if fallback_reason:
            span["fallback_reason"] = fallback_reason
        if output_accepted is not None:
            span["output_accepted"] = bool(output_accepted)
        if accepted_output_source:
            span["accepted_output_source"] = accepted_output_source
        return span

    response = _response_mapping_from_result(result)
    started = _started_at_from_response(response) or fallback_started_at_utc
    completed = _completed_at_from_response(response) or fallback_completed_at_utc
    transport_response = response.get("transport_response")
    nested_timing = (
        transport_response.get("transport_timing")
        if isinstance(transport_response, Mapping)
        else None
    )
    return build_provider_attempt_span(
        attempt_kind=attempt_kind,
        attempt_index=attempt_index,
        provider=str(getattr(result, "provider_requested", "") or ""),
        model=str(getattr(result, "model", "") or ""),
        provider_attempted=bool(getattr(result, "provider_attempted", False)),
        provider_available=bool(getattr(result, "provider_available", False)),
        runtime_generation_status=str(getattr(result, "runtime_generation_status", "") or ""),
        started_at_utc=started,
        completed_at_utc=completed,
        exact_provider_error=getattr(result, "exact_provider_error", None),
        section_id=section_id,
        fallback_reason=fallback_reason,
        output_accepted=output_accepted,
        accepted_output_source=accepted_output_source,
        transport_progress=response.get("transport_progress")
        if isinstance(response.get("transport_progress"), Mapping)
        else None,
        transport_timing=response.get("transport_timing")
        if isinstance(response.get("transport_timing"), Mapping)
        else nested_timing,
    )


def summarize_provider_attempt_spans(spans: list[dict[str, Any]]) -> dict[str, Any]:
    clean = [dict(span) for span in spans if isinstance(span, Mapping)]
    attempted = [span for span in clean if span.get("provider_attempted") is True]
    fallback = [span for span in clean if span.get("attempt_kind") == "fallback"]
    accepted = [
        span
        for span in clean
        if span.get("output_accepted") is True
        or str(span.get("runtime_generation_status") or "") == "REAL_LLM"
    ]
    durations = [
        span.get("duration_seconds")
        for span in clean
        if isinstance(span.get("duration_seconds"), (int, float))
    ]
    return {
        "schema_version": TIMING_SUMMARY_SCHEMA_VERSION,
        "span_count": len(clean),
        "attempted_count": len(attempted),
        "fallback_attempt_count": len(fallback),
        "fallback_attempted": bool(fallback),
        "providers": [str(span.get("provider") or "") for span in clean],
        "models": [str(span.get("model") or "") for span in clean],
        "runtime_generation_statuses": [
            str(span.get("runtime_generation_status") or "") for span in clean
        ],
        "total_duration_seconds": round(sum(float(v) for v in durations), 6)
        if durations
        else None,
        "accepted_output_provider": str(accepted[-1].get("provider") or "")
        if accepted
        else None,
        "accepted_output_model": str(accepted[-1].get("model") or "") if accepted else None,
    }


__all__ = [
    "SPAN_SCHEMA_VERSION",
    "TIMING_SUMMARY_SCHEMA_VERSION",
    "build_provider_attempt_span",
    "compact_transport_progress",
    "compact_transport_timing",
    "duration_seconds",
    "provider_result_attempt_span",
    "summarize_provider_attempt_spans",
    "utc_now_iso",
]
