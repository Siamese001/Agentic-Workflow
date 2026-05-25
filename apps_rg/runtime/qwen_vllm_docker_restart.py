"""Optional Docker restart for the local Qwen vLLM container before apps_rg live runs.

Best practice: **do not** restart on every invocation — that hides instability and adds
~tens of seconds per run while the model reloads. Default mode is ``if_unhealthy``:
call :func:`agentic_core.L2_execution.healers.vllm_health_probe.probe` on
``VLLM_BASE_URL``/``/v1/models`` and only run ``docker restart`` when the probe fails.

**W4:** When restart is opt-in and a restart is performed (or skipped as already healthy),
readiness is **fail-closed** against **HTTP** ``/v1/models``: TCP-only / non-200 / empty model
list / substring miss is **not** ready. Restart exit 0 alone is never sufficient.

Opt-in (operator workstation only):

    APPS_RG_QWEN_VLLM_DOCKER_RESTART=1

Optional:

    APPS_RG_QWEN_VLLM_CONTAINER_NAME   (default: local-qwen-vllm)
    APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE   if_unhealthy | always   (default: if_unhealthy)
    APPS_RG_QWEN_VLLM_DOCKER_CLI_TIMEOUT_SECONDS   (default: 240)
    APPS_RG_QWEN_VLLM_DOCKER_READY_WAIT_SECONDS    (default: 180)  — poll /v1/models after restart
    APPS_RG_QWEN_VLLM_DOCKER_READY_POLL_SECONDS    (default: 2.0)
    APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING   (default: Qwen; legacy: APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Any, Literal

from agentic_core.L0_routing.config.model_registry import VLLM_BASE_URL
from agentic_core.L2_execution.healers.vllm_health_probe import probe

from apps_rg.runtime.qwen_transport_diag import (
    READINESS_MODEL_MISMATCH,
    READINESS_MODEL_MISSING,
    READINESS_PROBE_FAILED,
    READINESS_READY,
    READINESS_RESTART_DISABLED,
    READINESS_RESTART_FAILED,
    READINESS_RESTART_NOT_REQUESTED,
    classify_vllm_models_readiness,
    expected_qwen_model_substring,
    fetch_openai_compatible_model_ids,
    redact_base_url_for_banner,
)

__all__ = ["maybe_restart_qwen_vllm_for_apps_rg_run"]

_RESTART_TRUTHY = frozenset({"1", "true", "yes", "on", "y"})
_DEFAULT_CONTAINER = "local-qwen-vllm"


def _env_truthy(name: str) -> bool:
    raw = str(os.environ.get(name, "") or "").strip().lower()
    return raw in _RESTART_TRUTHY


def _restart_mode() -> Literal["if_unhealthy", "always"]:
    raw = str(os.environ.get("APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE", "if_unhealthy") or "").strip().lower()
    if raw in ("always", "force", "yes_restart"):
        return "always"
    return "if_unhealthy"


def _float_env(name: str, default: float, *, lo: float, hi: float) -> float:
    try:
        v = float(os.environ.get(name, str(default)))
    except ValueError:
        v = default
    return max(lo, min(hi, v))


def _probe_timeout() -> float:
    try:
        return float(os.environ.get("VLLM_HEALTH_PROBE_TIMEOUT_SECONDS", "1.5"))
    except ValueError:
        return 1.5


def _should_skip_for_stub_or_mock(*, running_section_lane: bool, cli_provider: str | None) -> tuple[bool, str]:
    if _env_truthy("APPS_RG_L2_FORCE_STUB"):
        return True, "APPS_RG_L2_FORCE_STUB"
    mode = str(os.environ.get("APPS_RG_L2_PROVIDER_MODE", "") or "").strip().lower()
    if mode == "stub_only":
        return True, "APPS_RG_L2_PROVIDER_MODE=stub_only"
    if not running_section_lane:
        return False, ""
    from apps_rg.runtime.section_cli_defaults import (  # noqa: PLC0415
        SectionCliConfigError,
        resolve_cli_lane_provider_with_source,
    )

    try:
        prov, _src = resolve_cli_lane_provider_with_source(cli_provider)
    except SectionCliConfigError:
        return False, ""
    if str(prov).strip().lower() == "mock":
        return True, "section_lane_provider_mock"
    return False, ""


def _pack_audit(
    *,
    performed: bool,
    skipped: bool,
    reason: str,
    restart_requested: bool,
    restart_outcome: str,
    readiness_status: str,
    decisive_reason: str,
    post_restart_probe_status: str,
    observed_model_ids: list[str],
    attempt_count: int,
    ready: bool | None = None,
    **extra: Any,
) -> dict[str, Any]:
    rdy = ready if ready is not None else (readiness_status == READINESS_READY)
    exp = expected_qwen_model_substring()
    model_pick = ""
    for m in observed_model_ids:
        if exp in m:
            model_pick = m
            break
    if not model_pick and observed_model_ids:
        model_pick = observed_model_ids[0]
    out: dict[str, Any] = {
        "performed": performed,
        "skipped": skipped,
        "reason": reason,
        "restart_requested": restart_requested,
        "restart_outcome": restart_outcome,
        "post_restart_probe_status": post_restart_probe_status,
        "expected_model_substring": exp,
        "observed_model_ids": list(observed_model_ids),
        "readiness_status": readiness_status,
        "decisive_reason": decisive_reason,
        "base_url": redact_base_url_for_banner(str(VLLM_BASE_URL)),
        "probe_timeout_seconds": _probe_timeout(),
        "attempt_count": attempt_count,
        "ready": rdy,
        "probe_status": "healthy" if rdy else "unhealthy",
        "model_id": model_pick,
        "probe_error": None if rdy else decisive_reason,
        **extra,
    }
    return out


def maybe_restart_qwen_vllm_for_apps_rg_run(
    *,
    running_section_lane: bool,
    cli_provider: str | None,
) -> dict[str, Any]:
    """Run optional ``docker restart`` when configured and the vLLM probe warrants it.

    Never raises; returns an audit dict suitable for logging and W4 readiness artifacts.
    """
    if not _env_truthy("APPS_RG_QWEN_VLLM_DOCKER_RESTART"):
        return _pack_audit(
            performed=False,
            skipped=True,
            reason="not_configured",
            restart_requested=False,
            restart_outcome="restart_disabled",
            readiness_status=READINESS_RESTART_DISABLED,
            decisive_reason="APPS_RG_QWEN_VLLM_DOCKER_RESTART not enabled",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
        )

    skip, skip_reason = _should_skip_for_stub_or_mock(
        running_section_lane=running_section_lane,
        cli_provider=cli_provider,
    )
    if skip:
        return _pack_audit(
            performed=False,
            skipped=True,
            reason=skip_reason,
            restart_requested=True,
            restart_outcome="skipped",
            readiness_status=READINESS_RESTART_DISABLED,
            decisive_reason=f"docker_restart_skipped:{skip_reason}",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
        )

    container = str(os.environ.get("APPS_RG_QWEN_VLLM_CONTAINER_NAME", _DEFAULT_CONTAINER) or "").strip()
    if not container:
        container = _DEFAULT_CONTAINER

    mode = _restart_mode()
    pre = probe(force_refresh=True, base_url=VLLM_BASE_URL, timeout_seconds=_probe_timeout())

    if mode == "if_unhealthy" and pre.is_healthy:
        http_st, ids, terr = fetch_openai_compatible_model_ids(
            base_url=VLLM_BASE_URL, timeout_s=_probe_timeout()
        )
        rs, dr = classify_vllm_models_readiness(
            http_status=http_st,
            observed_model_ids=ids,
            expected_model_substring=expected_qwen_model_substring(),
            transport_error=terr,
        )
        post_probe = "healthy" if rs == READINESS_READY else "unhealthy"
        if rs != READINESS_READY:
            return _pack_audit(
                performed=False,
                skipped=True,
                reason="model_readiness_failed",
                restart_requested=True,
                restart_outcome="not_needed",
                readiness_status=rs,
                decisive_reason=dr,
                post_restart_probe_status=post_probe,
                observed_model_ids=ids,
                attempt_count=1,
                ready=False,
            )
        return _pack_audit(
            performed=False,
            skipped=True,
            reason="already_healthy",
            restart_requested=True,
            restart_outcome="not_needed",
            readiness_status=READINESS_RESTART_NOT_REQUESTED,
            decisive_reason="server_already_healthy_and_model_substring_ok",
            post_restart_probe_status="healthy",
            observed_model_ids=ids,
            attempt_count=1,
            ready=True,
        )

    if shutil.which("docker") is None:
        return _pack_audit(
            performed=False,
            skipped=False,
            reason="docker_cli_missing",
            restart_requested=True,
            restart_outcome="failed",
            readiness_status=READINESS_RESTART_FAILED,
            decisive_reason="docker not on PATH; cannot restart container",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
            error="docker not on PATH; cannot restart container",
        )

    cli_timeout = int(_float_env("APPS_RG_QWEN_VLLM_DOCKER_CLI_TIMEOUT_SECONDS", 240.0, lo=30.0, hi=600.0))
    try:
        proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- operator opt-in docker restart for local Qwen vLLM; not model inference egress
            ["docker", "restart", container],
            capture_output=True,
            text=True,
            timeout=float(cli_timeout),
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return _pack_audit(
            performed=False,
            skipped=False,
            reason="docker_restart_timeout",
            restart_requested=True,
            restart_outcome="failed",
            readiness_status=READINESS_RESTART_FAILED,
            decisive_reason=f"docker restart timed out after {cli_timeout}s",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
            error=f"docker restart timed out after {cli_timeout}s",
            container=container,
        )
    except OSError as exc:
        return _pack_audit(
            performed=False,
            skipped=False,
            reason="docker_restart_os_error",
            restart_requested=True,
            restart_outcome="failed",
            readiness_status=READINESS_RESTART_FAILED,
            decisive_reason=f"{type(exc).__name__}: {exc}",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
            error=f"{type(exc).__name__}: {exc}",
            container=container,
        )

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return _pack_audit(
            performed=False,
            skipped=False,
            reason="docker_restart_failed",
            restart_requested=True,
            restart_outcome="failed",
            readiness_status=READINESS_RESTART_FAILED,
            decisive_reason=err or f"docker restart exit {proc.returncode}",
            post_restart_probe_status="not_run",
            observed_model_ids=[],
            attempt_count=0,
            ready=False,
            error=err or f"exit {proc.returncode}",
            container=container,
        )

    wait_budget = int(_float_env("APPS_RG_QWEN_VLLM_DOCKER_READY_WAIT_SECONDS", 180.0, lo=5.0, hi=900.0))
    poll_s = _float_env("APPS_RG_QWEN_VLLM_DOCKER_READY_POLL_SECONDS", 2.0, lo=0.5, hi=30.0)
    deadline = time.monotonic() + float(wait_budget)
    attempt_count = 0
    last_ids: list[str] = []
    last_rs = READINESS_PROBE_FAILED
    last_dr = "probe_budget_exhausted"
    last_post = "unhealthy"
    while time.monotonic() < deadline:
        attempt_count += 1
        http_st, ids, terr = fetch_openai_compatible_model_ids(
            base_url=VLLM_BASE_URL, timeout_s=_probe_timeout()
        )
        last_ids = ids
        rs, dr = classify_vllm_models_readiness(
            http_status=http_st,
            observed_model_ids=ids,
            expected_model_substring=expected_qwen_model_substring(),
            transport_error=terr,
        )
        last_rs, last_dr = rs, dr
        last_post = "healthy" if rs == READINESS_READY else "unhealthy"
        if rs == READINESS_READY:
            return _pack_audit(
                performed=True,
                skipped=False,
                reason="restarted_and_ready",
                restart_requested=True,
                restart_outcome="success",
                readiness_status=READINESS_READY,
                decisive_reason=dr,
                post_restart_probe_status="healthy",
                observed_model_ids=ids,
                attempt_count=attempt_count,
                ready=True,
                container=container,
                restart_mode=mode,
                wait_cap_seconds=wait_budget,
            )
        time.sleep(poll_s)

    return _pack_audit(
        performed=True,
        skipped=False,
        reason="restarted_probe_exhausted",
        restart_requested=True,
        restart_outcome="success",
        readiness_status=last_rs,
        decisive_reason=last_dr,
        post_restart_probe_status=last_post,
        observed_model_ids=last_ids,
        attempt_count=attempt_count,
        ready=False,
        container=container,
        restart_mode=mode,
        wait_cap_seconds=wait_budget,
        probe_error=last_dr,
    )
