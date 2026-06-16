"""Competencies lane live-provider policy helpers (timeouts + audit shape).

The Qwen/vLLM HTTP reachability preflight was removed with the local-model provider; the
external generation provider owns its own transport and surfaces a BLOCKED ``ProviderResult``
on failure. Only the env-driven timeout/flag helpers, the status constants, and the audit
payload shape remain — consumed by the competencies lane for provenance.
"""
from __future__ import annotations

import os

STATUS_BLOCKED_LIVE_PROVIDER = "BLOCKED_LIVE_PROVIDER"
REASON_PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


def competencies_vllm_preflight_timeout_s() -> float:
    raw = os.environ.get("APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_TIMEOUT_SECONDS", "5")
    try:
        return max(0.5, min(float(raw), 30.0))
    except ValueError:
        return 5.0


def competencies_vllm_chat_timeout_s() -> int:
    """Chat/completions wall-clock budget for the competencies lane (transport only; not an X2 gate).

    Honors ``APPS_RG_COMPETENCIES_CHAT_TIMEOUT_SECONDS`` TRUTHFULLY. The prior hard 300s ceiling
    silently clamped an explicit 1000s E2E budget down to 300s — yet competencies is not a
    singleton call: it runs an 8-path self-consistency pool + Claude selector + possible regen
    rounds, which legitimately needs the larger wall-clock. The only ceiling now is the SHARED
    external-provider bound (``APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS``, default 1200s), so
    an operator-set budget is recorded into ``provider_request.json`` and used verbatim up to that
    safety bound. Default for unattended/normal runs stays a bounded 120s.
    """
    from apps_rg.runtime.providers.external_provider import external_provider_timeout_max_s

    raw = os.environ.get("APPS_RG_COMPETENCIES_CHAT_TIMEOUT_SECONDS", "120")
    ceiling = external_provider_timeout_max_s()
    try:
        return int(max(60.0, min(float(raw), ceiling)))
    except (TypeError, ValueError):
        return 120


def competencies_vllm_preflight_disabled() -> bool:
    return os.environ.get("APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_DISABLE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def live_provider_gate_audit_payload_failure(
    *,
    provider_base_url: str,
    preflight_detail: str,
    timeout_s: float,
    probe_snapshot: dict[str, object] | None = None,
) -> dict[str, object]:
    snap = dict(probe_snapshot) if isinstance(probe_snapshot, dict) else None
    return {
        "live_provider_gate_status": STATUS_BLOCKED_LIVE_PROVIDER,
        "provider_unreachable_reason": REASON_PROVIDER_UNAVAILABLE,
        "preflight_transport": "external_provider",
        "provider_base_url": provider_base_url,
        "preflight_detail": preflight_detail,
        "preflight_error_detail": preflight_detail,
        "probe_snapshot": snap,
        "preflight_timeout_seconds": timeout_s,
        "http_post_attempted": False,
    }
