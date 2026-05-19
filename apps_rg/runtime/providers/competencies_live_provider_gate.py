"""Fail-fast HTTP /v1/models reachability gate for competencies ``qwen_vllm`` live runs.

Uses the same probe primitive as other section lanes (``vllm_health_probe.probe`` via
``apps_rg.runtime.qwen_transport_diag.run_http_models_preflight``).

Stub/offline contract runs bypass live preflight at dispatch (see ``competencies_dispatch``).
"""
from __future__ import annotations

import os
import socket
from urllib.parse import urlparse

from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
from apps_rg.runtime.qwen_transport_diag import run_http_models_preflight

STATUS_BLOCKED_LIVE_PROVIDER = "BLOCKED_LIVE_PROVIDER"
REASON_PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


def competencies_vllm_preflight_timeout_s() -> float:
    raw = os.environ.get("APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_TIMEOUT_SECONDS", "5")
    try:
        return max(0.5, min(float(raw), 30.0))
    except ValueError:
        return 5.0


def competencies_vllm_chat_timeout_s() -> int:
    """Chat/completions timeout for competencies lane (transport only; not an X2 gate)."""
    raw = os.environ.get("APPS_RG_COMPETENCIES_QWEN_CHAT_TIMEOUT_SECONDS", "120")
    try:
        return int(max(60, min(float(raw), 300.0)))
    except ValueError:
        return 120


def competencies_vllm_preflight_disabled() -> bool:
    return os.environ.get("APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_DISABLE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def qwen_openai_base_tcp_preflight(*, provider_url: str, timeout_s: float | None = None) -> tuple[bool, str]:
    """Try TCP connect to ``host:port`` inferred from *provider_url*.

    **Legacy helper** retained for unit tests; live competencies gate uses
    :func:`qwen_vllm_http_models_preflight`.
    """
    if timeout_s is None:
        timeout_s = competencies_vllm_preflight_timeout_s()
    trimmed = str(provider_url).strip()
    if not trimmed:
        return False, "empty provider_url"
    parsed = urlparse(trimmed)
    host = parsed.hostname
    if not host:
        return False, f"no hostname in URL: {trimmed!r}"
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    try:
        with socket.create_connection((host, int(port)), timeout=float(timeout_s)):
            pass
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, ""


def qwen_vllm_http_models_preflight(
    *, provider_url: str, timeout_s: float | None = None
) -> tuple[bool, str, dict[str, object]]:
    """HTTP GET ``{base}/v1/models`` probe (shared shape with section slice).

    Returns ``(ok, detail, probe_snapshot)`` where *detail* is empty on success.
    """
    if timeout_s is None:
        timeout_s = competencies_vllm_preflight_timeout_s()
    ok, snap, code = run_http_models_preflight(base_url=provider_url, timeout_s=float(timeout_s))
    snap_obj: dict[str, object] = {str(k): v for k, v in snap.items()}
    if ok:
        return True, "", snap_obj
    detail = str((snap or {}).get("error") or code or "probe_failed")
    return False, detail, snap_obj


def blocked_live_provider_preflight_result(
    *,
    model: str,
    base_url: str,
    preflight_detail: str,
    timeout_s: float,
    probe_snapshot: dict[str, object] | None = None,
) -> ProviderResult:
    """Synthetic provider row when HTTP models preflight fails (no chat/completions POST)."""
    err = (
        f"{STATUS_BLOCKED_LIVE_PROVIDER}: {REASON_PROVIDER_UNAVAILABLE} — "
        f"HTTP /v1/models preflight failed for endpoint derived from {base_url!r} within {timeout_s}s ({preflight_detail}). "
        "No chat/completions POST attempted."
    )
    return ProviderResult(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_available=False,
        exact_provider_error=err,
        runtime_generation_status="BLOCKED",
        model=str(model),
        raw_model_output="",
        provider_response=None,
        apps_rg_qwen_preflight_blocked=True,
        apps_rg_last_probe_snapshot=dict(probe_snapshot) if isinstance(probe_snapshot, dict) else None,
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
        "preflight_transport": "http_v1_models",
        "provider_base_url": provider_base_url,
        "preflight_detail": preflight_detail,
        "preflight_error_detail": preflight_detail,
        "tcp_error_detail": preflight_detail,
        "probe_snapshot": snap,
        "preflight_timeout_seconds": timeout_s,
        "http_post_attempted": False,
    }
