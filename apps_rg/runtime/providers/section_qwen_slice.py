"""W3 consolidated Qwen slice — single entry + governed reasoning receipts for section lanes."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from agentic_core.runtime.reasoning.reasoning_control_resolver import resolve_gateway_receipt
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities

from apps_rg.runtime.providers import qwen_vllm_provider
from apps_rg.runtime.providers.competencies_live_provider_gate import (
    REASON_PROVIDER_UNAVAILABLE,
    STATUS_BLOCKED_LIVE_PROVIDER,
    competencies_vllm_preflight_timeout_s,
)
from apps_rg.runtime.qwen_transport_diag import ensure_http_preflight_and_banner_for_slice
from apps_rg.runtime.reasoning.apps_rg_http_reasoning_plan import build_apps_rg_http_reasoning_plan
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    profile_to_requested_kw,
    section_reasoning_profile,
)

__all__ = ["call_qwen_vllm", "tag_reasoning_lane"]

_ALLOWED_HTTP_CHAT: Final[frozenset[str]] = frozenset(
    {"model", "messages", "temperature", "max_tokens", "timeout_seconds", "response_format"},
)
_TRANSPORT_FORWARDED: Final[frozenset[str]] = frozenset({"temperature", "max_tokens"})
_ORCH_PAYLOAD_KEYS: Final[frozenset[str]] = frozenset(
    {
        "self_consistency_samples",
        "tot_branches",
        "tot_depth",
        "reflexion_loops",
        "cot_paths",
    },
)
_FORBIDDEN_SCRATCH: Final[frozenset[str]] = frozenset({"scratchpad", "reveal_scratchpad"})


def tag_reasoning_lane(payload: Mapping[str, Any], lane_key: str) -> dict[str, Any]:
    merged = dict(payload)
    merged["_reasoning_section_lane"] = str(lane_key)
    return merged


def _sanitize_transport_payload(pd: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in dict(pd).items():
        ks = str(k)
        if ks in _FORBIDDEN_SCRATCH:
            raise ValueError(f"scratchpad_keys_forbidden_on_vllm_transport:{ks}")
        if ks.startswith("_"):
            continue
        if ks in _ORCH_PAYLOAD_KEYS:
            continue
        if ks not in _ALLOWED_HTTP_CHAT:
            continue
        out[ks] = v
    return out


def call_qwen_vllm(
    payload: dict[str, Any],
    /,
    *,
    artifact_dir: Path | str | None = None,
    run_id: str | None = None,
    temperature_override: float | None = None,
) -> qwen_vllm_provider.ProviderResult:
    envelope = dict(payload)
    lane_token = envelope.pop("_reasoning_section_lane", None)
    lane_s = str(lane_token).strip().lower() if lane_token else None

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    if artifact_dir is not None:
        merge_transport_context(artifact_dir=str(Path(artifact_dir).resolve()))
    if run_id is not None:
        merge_transport_context(run_id=str(run_id))
    if lane_s:
        merge_transport_context(section_lane=lane_s)

    profile = section_reasoning_profile(lane_s)
    prof_kw = profile_to_requested_kw(profile)

    merged_req: dict[str, Any] = {**prof_kw}
    mt = envelope.get("max_tokens")
    if mt is not None:
        merged_req["max_tokens"] = mt

    http_body = _sanitize_transport_payload(envelope)
    if temperature_override is not None:
        http_body["temperature"] = float(temperature_override)
    else:
        http_body["temperature"] = float(prof_kw["temperature"])

    for leak in _FORBIDDEN_SCRATCH:
        if leak in http_body:
            raise ValueError(f"forbidden_scratch_key_in_transport:{leak}")

    try:
        plan = build_apps_rg_http_reasoning_plan(merged_requested_kw=merged_req, profile=profile)
        caps = TransportCapabilities(_TRANSPORT_FORWARDED)
        observed = {k: http_body[k] for k in _TRANSPORT_FORWARDED if k in http_body}
        rec_obj = resolve_gateway_receipt(plan, caps, observed)
        receipt_prim = rec_obj.to_primitive()
    except (ArithmeticError, TypeError, ValueError):
        receipt_prim = None

    base_url = str(os.environ.get("VLLM_BASE_URL", qwen_vllm_provider.DEFAULT_QWEN_BASE_URL))
    pre_timeout = float(competencies_vllm_preflight_timeout_s())
    ok_pre, pre_snap, pre_code = ensure_http_preflight_and_banner_for_slice(
        base_url=base_url,
        timeout_seconds=pre_timeout,
    )
    if not ok_pre:
        msg = (
            f"{STATUS_BLOCKED_LIVE_PROVIDER}: {REASON_PROVIDER_UNAVAILABLE} — "
            f"HTTP /v1/models preflight failed for {base_url!r} ({pre_code}). "
            "No chat/completions POST attempted."
        )
        return qwen_vllm_provider.ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error=msg,
            runtime_generation_status="BLOCKED",
            model=str(http_body.get("model", qwen_vllm_provider.DEFAULT_QWEN_MODEL)),
            raw_model_output="",
            provider_response=None,
            reasoning_execution_receipt=receipt_prim,
            apps_rg_qwen_preflight_blocked=True,
            apps_rg_last_probe_snapshot=pre_snap if isinstance(pre_snap, dict) else None,
        )

    result = qwen_vllm_provider.call_qwen_vllm(http_body, base_url=base_url)
    result.reasoning_execution_receipt = receipt_prim
    return result
