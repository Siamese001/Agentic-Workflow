"""W3 consolidated Qwen slice — single entry + governed reasoning receipts for section lanes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from agentic_core.runtime.reasoning.reasoning_control_resolver import resolve_gateway_receipt
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities

from apps_rg.runtime.reasoning.apps_rg_http_reasoning_plan import build_apps_rg_http_reasoning_plan
from apps_rg.runtime.providers import qwen_vllm_provider
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


def call_qwen_vllm(payload: dict[str, Any], /) -> qwen_vllm_provider.ProviderResult:
    envelope = dict(payload)
    lane_token = envelope.pop("_reasoning_section_lane", None)
    lane_s = str(lane_token).strip().lower() if lane_token else None

    profile = section_reasoning_profile(lane_s)
    prof_kw = profile_to_requested_kw(profile)

    merged_req: dict[str, Any] = {**prof_kw}
    mt = envelope.get("max_tokens")
    if mt is not None:
        merged_req["max_tokens"] = mt

    http_body = _sanitize_transport_payload(envelope)
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

    result = qwen_vllm_provider.call_qwen_vllm(http_body)
    result.reasoning_execution_receipt = receipt_prim
    return result
