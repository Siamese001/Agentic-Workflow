"""Artifact-safe diagnostics for apps_rg live Qwen/vLLM HTTP transport (W1–W4).

No secrets, Authorization headers, prompts, or raw chat payloads in emitted JSON.
"""

from __future__ import annotations

import errno
import json
import os
import re
import time
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlsplit
import urllib.error
import urllib.request

from agentic_core.L2_execution.healers.vllm_health_probe import VLLMHealth, probe

from apps_rg.runtime.artifact_secret_redaction import redact_sensitive_mapping

from apps_rg.runtime.qwen_offline_contract_stub import (
    OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
    effective_offline_contract_stub_enabled,
)

_TRANS_CTX: ContextVar[dict[str, Any] | None] = ContextVar("apps_rg_qwen_transport_ctx", default=None)
_SLICING_DONE: ContextVar[frozenset[str] | None] = ContextVar("apps_rg_qwen_slice_http_done", default=None)

ENV_QWEN_READY_SUBSTRING: Final[str] = "APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING"
# W4 primary SSOT for substring checks (defaults to Qwen when unset). Legacy alias: ENV_QWEN_READY_SUBSTRING.
ENV_EXPECTED_MODEL_SUBSTRING: Final[str] = "APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING"
DOCKER_RESTART_READINESS_FILENAME: Final[str] = "qwen_vllm_docker_restart_readiness.json"

# Post-restart / pre-run readiness taxonomy (docker opt-in path only).
READINESS_RESTART_DISABLED: Final[str] = "restart_disabled"
READINESS_RESTART_NOT_REQUESTED: Final[str] = "restart_not_requested"
READINESS_RESTART_FAILED: Final[str] = "restart_failed"
READINESS_PROBE_FAILED: Final[str] = "probe_failed"
READINESS_MODEL_MISSING: Final[str] = "model_missing"
READINESS_MODEL_MISMATCH: Final[str] = "model_mismatch"
READINESS_READY: Final[str] = "ready"

ERR_TCP_CONNECT: Final[str] = "tcp_connect_failure"
ERR_HTTP_MODELS_PROBE: Final[str] = "http_v1_models_probe_failure"
ERR_WRONG_MISSING_MODEL_ID: Final[str] = "wrong_or_missing_model_id"
ERR_CHAT_TIMEOUT: Final[str] = "chat_completion_timeout"
ERR_CHAT_5XX: Final[str] = "chat_completion_5xx"
ERR_CHAT_4XX: Final[str] = "chat_non_retryable_4xx"
ERR_MALFORMED_RESPONSE: Final[str] = "malformed_response"
ERR_UNKNOWN: Final[str] = "unknown"
# Chat eventually succeeded after transient transport retries (informational — not a failure).
ERR_TRANSPORT_RECOVERED: Final[str] = "transport_recovered"

SIDECAR_NAME: Final[str] = "qwen_transport_diagnostic.json"
BANNER_PREFIX: Final[str] = "APPS_RG_QWEN_LIVE"

# W3: bounded transient transport retry (chat/completions only — not probe heal)
RETRY_POLICY_NAME: Final[str] = "apps_rg_qwen_vllm_transport_transient"
RETRY_POLICY_VERSION: Final[str] = "1"
ENV_TRANSPORT_MAX_ATTEMPTS: Final[str] = "APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS"
ENV_TRANSPORT_BACKOFF_BASE_S: Final[str] = "APPS_RG_QWEN_TRANSPORT_RETRY_BACKOFF_BASE_S"
ENV_TRANSPORT_BACKOFF_CAP_S: Final[str] = "APPS_RG_QWEN_TRANSPORT_RETRY_BACKOFF_CAP_S"


def _truthy(raw: str | None) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on", "y"}


def set_docker_restart_audit(audit: dict[str, Any] | None) -> None:
    """Record CLI docker-restart outcome for banners and diagnostics."""
    merge_transport_context(docker_restart_audit=dict(audit) if audit else None)


def merge_transport_context(**kwargs: Any) -> None:
    cur = dict(_TRANS_CTX.get() or {})
    for k, v in kwargs.items():
        if v is not None:
            cur[k] = v
    _TRANS_CTX.set(cur)


def get_transport_context() -> dict[str, Any]:
    return dict(_TRANS_CTX.get() or {})


def reset_transport_context_for_tests() -> None:
    """Clear contextvars (unit tests only)."""
    _TRANS_CTX.set(None)
    _SLICING_DONE.set(None)


def models_probe_url(base_url: str) -> str:
    return str(base_url).rstrip("/") + "/models"


def redact_base_url_for_banner(url: str) -> str:
    """Host + port + path root only; strip query, obscure rare auth in path."""
    parts = urlsplit(str(url).strip())
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    path = (parts.path or "").rstrip("/")
    root = path.split("/")[0] if path else ""
    path_prefix = f"/{root}" if root else ""
    return f"{parts.scheme}://{host}{port}{path_prefix}/…" if host else "<invalid>"


def expected_qwen_model_substring() -> str:
    """Expected substring for a valid Qwen model id in ``/v1/models`` (W4).

    ``APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING`` wins when set (including empty -> fall back to ``Qwen``).
    Otherwise ``APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING`` is used for backward compatibility.
    """
    if os.environ.get(ENV_EXPECTED_MODEL_SUBSTRING) is not None:
        s = str(os.environ.get(ENV_EXPECTED_MODEL_SUBSTRING, "") or "").strip()
        return s if s else "Qwen"
    legacy = os.environ.get(ENV_QWEN_READY_SUBSTRING)
    if legacy is not None:
        s2 = str(legacy or "").strip()
        return s2 if s2 else "Qwen"
    return "Qwen"


def fetch_openai_compatible_model_ids(*, base_url: str, timeout_s: float) -> tuple[int | None, list[str], str | None]:
    """GET ``/v1/models`` and return ``(http_status, model_ids, transport_error)``.

    On connection/timeout/parse failures, ``http_status`` may be None and ``transport_error`` is set.
    Does not send auth headers. No prompt payload.
    """
    url = str(base_url).rstrip("/") + "/models"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=float(timeout_s)) as resp:
            code = int(resp.getcode())
            if code != 200:
                return code, [], None
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            exc.read()
        except OSError:
            pass
        return int(exc.code), [], None
    except urllib.error.URLError as exc:
        return None, [], f"url_error:{getattr(exc, 'reason', exc)!s}"
    except TimeoutError as exc:
        return None, [], f"timeout:{exc!s}"
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, [], f"{type(exc).__name__}:{exc!s}"

    data = payload.get("data") if isinstance(payload, dict) else None
    rows = data if isinstance(data, list) else []
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        mid = row.get("id")
        if mid is None:
            continue
        ids.append(str(mid).strip())
    return 200, ids, None


def classify_vllm_models_readiness(
    *,
    http_status: int | None,
    observed_model_ids: list[str],
    expected_model_substring: str,
    transport_error: str | None,
) -> tuple[str, str]:
    """Fail closed: TCP-only / non-200 / empty ids / substring miss -> not ready.

    Returns ``(readiness_status, decisive_reason)`` using W4 taxonomy strings.
    """
    if transport_error:
        return READINESS_PROBE_FAILED, transport_error[:500]
    if http_status is None:
        return READINESS_PROBE_FAILED, "no_http_response"
    if http_status != 200:
        return READINESS_PROBE_FAILED, f"http_status_{http_status}"
    normalized = [str(x).strip() for x in observed_model_ids if str(x).strip()]
    if not normalized:
        return READINESS_MODEL_MISSING, "models_response_missing_nonempty_ids"
    exp = str(expected_model_substring or "").strip() or "Qwen"
    if not any(exp in mid for mid in normalized):
        return READINESS_MODEL_MISMATCH, f"expected_substring_not_in_any_model_id:{exp!r}"
    return READINESS_READY, "model_id_matches_expected_substring"


def persist_docker_restart_readiness_artifact(artifact_dir: Path | str, audit: dict[str, Any]) -> Path | None:
    """Write redacted docker-restart readiness record under ``artifact_dir`` (best-effort)."""
    raw = str(artifact_dir).strip()
    if not raw:
        return None
    base = Path(raw)
    base.mkdir(parents=True, exist_ok=True)
    doc: dict[str, Any] = {"schema": "apps_rg.qwen_vllm_docker_restart_readiness.v1", **audit}
    out = redact_sensitive_mapping(doc)
    path = base / DOCKER_RESTART_READINESS_FILENAME
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def probe_to_snapshot(health: VLLMHealth, *, probe_url_s: str) -> dict[str, Any]:
    return {
        "probe_url": probe_url_s,
        "status": health.status,
        "model_id": health.model_id,
        "latency_ms": health.latency_ms,
        "error": health.error,
        "checked_at": health.checked_at,
    }


def redacted_exception_message(exc: BaseException | None, http_body_fragment: str = "") -> str:
    """Strip likely secrets from error text."""
    raw = " ".join(
        x
        for x in (
            f"{type(exc).__name__}: {exc}" if exc is not None else "",
            http_body_fragment[:400] if http_body_fragment else "",
        )
        if x
    )
    out = re.sub(r"(?i)(bearer|api[_-]?key|token)\s*[:=]\s*\S+", r"\1=<redacted>", raw)
    out = re.sub(r"(?i)bearer\s+[a-z0-9_\-]{3,}\b", "Bearer <redacted>", out)
    out = re.sub(r"(?i)sk-[a-z0-9]{10,}", "sk-<redacted>", out)
    out = re.sub(r'(?i)"content"\s*:\s*"[^"]*"', '"content":"<redacted>"', out)
    out = re.sub(r"(?i)messages\s*=\s*\[[^\]]{8,}\]", "messages=<redacted>", out)
    return out[:2000]


def classify_http_error(*, code: int | None) -> str | None:
    if code is None:
        return None
    if 500 <= code <= 599:
        return ERR_CHAT_5XX
    if 400 <= code <= 499:
        return ERR_CHAT_4XX
    return None


def max_transport_attempts() -> int:
    """Total chat attempts including the first. Default 3 (initial + 2 retries). Capped."""
    raw = os.environ.get(ENV_TRANSPORT_MAX_ATTEMPTS, "3")
    try:
        n = int(raw)
    except ValueError:
        n = 3
    return max(1, min(n, 5))


def transport_retry_backoff_seconds(attempt_after_failure_index: int) -> float:
    """attempt_after_failure_index: 0 after first failure (before 2nd try), then 1, …"""
    try:
        base = float(os.environ.get(ENV_TRANSPORT_BACKOFF_BASE_S, "0.25"))
    except ValueError:
        base = 0.25
    try:
        cap = float(os.environ.get(ENV_TRANSPORT_BACKOFF_CAP_S, "1.5"))
    except ValueError:
        cap = 1.5
    return min(cap, max(0.0, base) * (2 ** max(0, attempt_after_failure_index)))


def is_transient_chat_http_status(code: int) -> bool:
    """Narrow retriable HTTP statuses for chat/completions only (not proof weakening)."""
    return code in {408, 429, 502, 503, 504}


def is_transient_url_error(exc: urllib.error.URLError) -> bool:
    reason = getattr(exc, "reason", None)
    if isinstance(reason, TimeoutError):
        return True
    if isinstance(reason, OSError):
        errn = getattr(reason, "errno", None)
        if errn in {
            errno.ECONNREFUSED,
            errno.ECONNRESET,
            errno.ETIMEDOUT,
            errno.ENETUNREACH,
            errno.EHOSTUNREACH,
        }:
            return True
        if isinstance(reason, (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return True
    msg = str(reason or exc).lower()
    if any(
        s in msg
        for s in (
            "timed out",
            "timeout",
            "connection refused",
            "connection reset",
            "reset by peer",
            "broken pipe",
            "temporarily unavailable",
        )
    ):
        return True
    return False


def docker_restart_banner_label(audit: dict[str, Any] | None) -> str:
    if not _truthy(os.environ.get("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "")):
        return "disabled"
    if not audit:
        return "not_applicable"
    if audit.get("skipped"):
        reason = str(audit.get("reason") or "")
        if reason == "not_configured":
            return "disabled"
        if reason in {"offline_contract_stub", "section_lane_provider_mock", "APPS_RG_L2_FORCE_STUB"}:
            return "not_applicable"
        if reason == "already_healthy":
            return "not_applicable"
        if reason == "model_readiness_failed":
            return "failed"
    if audit.get("performed") and audit.get("ready"):
        return "succeeded"
    if audit.get("performed") and not audit.get("ready"):
        return "failed"
    if not audit.get("skipped") and audit.get("error"):
        return "failed"
    return "requested"


def run_http_models_preflight(
    *,
    base_url: str,
    timeout_s: float,
    force_refresh: bool = True,
) -> tuple[bool, dict[str, Any], str | None]:
    """GET /v1/models style probe; optionally require Qwen substring in model id.

    Returns (ok, probe_snapshot, failure_code).
    """
    pu_url = models_probe_url(base_url)
    health = probe(
        base_url=base_url,
        force_refresh=force_refresh,
        timeout_seconds=float(timeout_s),
    )
    snap = probe_to_snapshot(health, probe_url_s=pu_url)
    if not health.is_healthy:
        return False, snap, ERR_HTTP_MODELS_PROBE
    sub = expected_qwen_model_substring()
    if sub and sub not in (health.model_id or ""):
        return False, snap, ERR_WRONG_MISSING_MODEL_ID
    return True, snap, None


def build_sidecar_document(
    *,
    effective_base_url: str,
    probe_snapshot: dict[str, Any] | None,
    error_category: str,
    http_status: int | None,
    exception_type: str | None,
    redacted_message: str,
    timeout_seconds: float | int,
    attempt_count: int,
    retry_reasons: list[str],
    run_id: str | None,
    section_lane: str | None,
    mock_or_stub_used: bool,
    docker_restart_requested_outcome: str | None = None,
    attempts: list[dict[str, Any]] | None = None,
    final_error_category: str | None = None,
    retried: bool = False,
    retry_policy_name: str | None = None,
    retry_policy_version: str | None = None,
    model: str | None = None,
    runtime_generation_status: str | None = None,
) -> dict[str, Any]:
    audit = get_transport_context().get("docker_restart_audit")
    fin_cat = final_error_category if final_error_category else error_category
    att_list = list(attempts) if attempts else []
    return {
        "schema": "apps_rg.qwen_transport_diagnostic.v2",
        "run_id": run_id,
        "section_lane": section_lane,
        "provider_lane": "qwen_vllm",
        "model": model,
        "effective_base_url": effective_base_url,
        "probe_url": models_probe_url(effective_base_url),
        "probe_snapshot": probe_snapshot,
        "error_category": error_category,
        "final_error_category": fin_cat,
        "http_status": http_status,
        "exception_type": exception_type,
        "redacted_message": redacted_message,
        "timeout_seconds": timeout_seconds,
        "attempted_at": time.time(),
        "attempt_count": attempt_count,
        "attempts": att_list,
        "retry_reasons": list(retry_reasons),
        "retried": bool(retried),
        "retry_policy_name": retry_policy_name,
        "retry_policy_version": retry_policy_version,
        "mock_or_stub_used": bool(mock_or_stub_used),
        "docker_restart_requested_outcome": docker_restart_requested_outcome,
        "runtime_generation_status": runtime_generation_status,
        "diagnostic_id": str(uuid.uuid4()),
    }


def write_sidecar(artifact_dir: Path, doc: dict[str, Any]) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / SIDECAR_NAME
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def emit_live_banner(
    *,
    base_url: str,
    probe_label: str,
) -> None:
    eff = get_transport_context().get("docker_restart_audit")
    rlab = docker_restart_banner_label(eff if isinstance(eff, dict) else None)
    print(
        f"{BANNER_PREFIX} provider=qwen_vllm base_url={redact_base_url_for_banner(base_url)} "
        f"restart={rlab} probe={probe_label}",
        flush=True,
    )


def _slice_session_key(base_url: str) -> str:
    ctx = get_transport_context()
    return "|".join(
        (
            str(ctx.get("artifact_dir") or ""),
            str(ctx.get("run_id") or ""),
            str(base_url).strip(),
        )
    )


def ensure_http_preflight_and_banner_for_slice(
    *,
    base_url: str,
    timeout_seconds: float | int,
) -> tuple[bool, dict[str, Any] | None, str | None]:
    """Run /v1/models probe once per (artifact_dir, run_id, base_url); emit banner once.

    When effective offline stub is on, skip network (returns ok=True, no probe).
    Returns ``(ok, probe_snapshot_on_success_or_failure, failure_code)``.
    """
    if effective_offline_contract_stub_enabled():
        return True, None, None

    key = _slice_session_key(base_url)
    done = _SLICING_DONE.get()
    if done is not None and key in done:
        return True, None, None

    from apps_rg.runtime.providers.competencies_live_provider_gate import (  # noqa: PLC0415
        competencies_vllm_preflight_disabled,
    )

    lane = str(get_transport_context().get("section_lane") or "").strip().lower()
    if lane == "competencies" and competencies_vllm_preflight_disabled():
        emit_live_banner(base_url=base_url, probe_label="not_run")
        _SLICING_DONE.set(frozenset((done or frozenset()) | {key}))
        return True, None, None

    ok, snap, code = run_http_models_preflight(base_url=base_url, timeout_s=float(timeout_seconds))
    probe_lbl = "pass" if ok else "fail"
    emit_live_banner(base_url=base_url, probe_label=probe_lbl)

    new_done = frozenset((done or frozenset()) | {key})
    _SLICING_DONE.set(new_done)

    if ok:
        return True, snap, None

    ctx = get_transport_context()
    doc = build_sidecar_document(
        effective_base_url=base_url,
        probe_snapshot=snap,
        error_category=str(code or ERR_HTTP_MODELS_PROBE),
        http_status=None,
        exception_type=None,
        redacted_message=str(snap.get("error") or code or ""),
        timeout_seconds=timeout_seconds,
        attempt_count=1,
        retry_reasons=[],
        run_id=ctx.get("run_id") if isinstance(ctx.get("run_id"), str) else None,
        section_lane=ctx.get("section_lane") if isinstance(ctx.get("section_lane"), str) else None,
        mock_or_stub_used=False,
        docker_restart_requested_outcome=docker_restart_banner_label(ctx.get("docker_restart_audit")),
        attempts=[],
        final_error_category=str(code or ERR_HTTP_MODELS_PROBE),
        retried=False,
        retry_policy_name=None,
        retry_policy_version=None,
        model=None,
        runtime_generation_status=None,
    )
    ad = ctx.get("artifact_dir")
    if ad:
        write_sidecar(Path(str(ad)), doc)
    return False, snap, code


def persist_success_after_transport_retries(
    *,
    base_url: str,
    timeout_seconds: float | int,
    attempt_count: int,
    retry_reasons: list[str],
    attempts: list[dict[str, Any]],
    model: str,
    probe_snapshot: dict[str, Any] | None = None,
) -> None:
    """Write diagnostic sidecar when chat succeeded after transient transport retries (REAL_LLM only).

    Does not run for offline contract stub; does not imply stub/mock fallback.
    """
    if effective_offline_contract_stub_enabled():
        return
    ctx = get_transport_context()
    ad = ctx.get("artifact_dir")
    if not ad:
        return
    rr = list(retry_reasons)
    if not rr:
        return
    audit = ctx.get("docker_restart_audit") if isinstance(ctx.get("docker_restart_audit"), dict) else None
    doc = build_sidecar_document(
        effective_base_url=base_url,
        probe_snapshot=probe_snapshot,
        error_category=ERR_TRANSPORT_RECOVERED,
        http_status=None,
        exception_type=None,
        redacted_message="chat_completions succeeded after transient transport retries",
        timeout_seconds=timeout_seconds,
        attempt_count=attempt_count,
        retry_reasons=rr,
        run_id=str(ctx.get("run_id") or "") or None,
        section_lane=str(ctx.get("section_lane") or "") or None,
        mock_or_stub_used=False,
        docker_restart_requested_outcome=docker_restart_banner_label(audit),
        attempts=list(attempts),
        final_error_category=ERR_TRANSPORT_RECOVERED,
        retried=True,
        retry_policy_name=RETRY_POLICY_NAME,
        retry_policy_version=RETRY_POLICY_VERSION,
        model=model,
        runtime_generation_status="REAL_LLM",
    )
    write_sidecar(Path(str(ad)), doc)


def persist_failure_for_provider_result(
    *,
    result: Any,
    base_url: str,
    timeout_seconds: float | int,
    exception: BaseException | None,
    http_status: int | None,
    body_fragment: str,
    error_category: str,
    probe_snapshot: dict[str, Any] | None,
    attempt_count: int = 1,
    retry_reasons: list[str] | None = None,
    attempts: list[dict[str, Any]] | None = None,
    final_error_category: str | None = None,
    retried: bool = False,
    model: str | None = None,
) -> None:
    if getattr(result, "provider_requested", "") != "qwen_vllm":
        return
    rgs = getattr(result, "runtime_generation_status", "")
    if rgs in ("MOCKED", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS):
        return
    if getattr(result, "provider_available", False) and rgs == "REAL_LLM":
        return
    ctx = get_transport_context()
    ad = ctx.get("artifact_dir")
    if not ad:
        return
    audit = ctx.get("docker_restart_audit") if isinstance(ctx.get("docker_restart_audit"), dict) else None
    rr = list(retry_reasons) if retry_reasons else []
    doc = build_sidecar_document(
        effective_base_url=base_url,
        probe_snapshot=probe_snapshot,
        error_category=error_category,
        http_status=http_status,
        exception_type=type(exception).__name__ if exception is not None else None,
        redacted_message=redacted_exception_message(exception, body_fragment),
        timeout_seconds=timeout_seconds,
        attempt_count=attempt_count,
        retry_reasons=rr,
        run_id=str(ctx.get("run_id") or "") or None,
        section_lane=str(ctx.get("section_lane") or "") or None,
        mock_or_stub_used=False,
        docker_restart_requested_outcome=docker_restart_banner_label(audit),
        attempts=list(attempts) if attempts else [],
        final_error_category=final_error_category,
        retried=retried,
        retry_policy_name=RETRY_POLICY_NAME if (retried or attempt_count > 1) else None,
        retry_policy_version=RETRY_POLICY_VERSION if (retried or attempt_count > 1) else None,
        model=model,
        runtime_generation_status=rgs or None,
    )
    write_sidecar(Path(str(ad)), doc)
