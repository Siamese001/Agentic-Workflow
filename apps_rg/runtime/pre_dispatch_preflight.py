"""Mandatory fail-closed pre-dispatch checks for ``python -m apps_rg --section <lane>``.

Runs before lane runtime, docker restart, and ``canonical_dispatch``. Emits a preflight
receipt that records whether dispatch actually started.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from apps_rg.runtime.briefing_resolution import _looks_like_filesystem_ref as _briefing_looks_like_path
from apps_rg.runtime.briefing_ssot import DEFAULT_TARGETING_BRIEFING_PATH
from apps_rg.runtime.jd_resolution import DEFAULT_JD_TARGETING_PATH, _looks_like_filesystem_ref as _jd_looks_like_path
from apps_rg.runtime.runtime_proof_layout import find_repo_root
from apps_rg.runtime.targeting_input_freshness import (
    is_stale_default_targeting_briefing,
    is_stale_default_targeting_jd,
)

TargetingInputStatus = Literal["PASS", "MISSING", "EMPTY", "STALE", "DEFAULT_BLOCKED"]
QwenGateStatus = Literal["PASS", "FAIL", "SKIPPED", "NOT_APPLICABLE"]
UpstreamBulletsGateStatus = Literal["NOT_APPLICABLE", "PASS", "BLOCKED"]

_ENV_ALLOW_STALE_TARGETING_SSOT = "APPS_RG_ALLOW_STALE_TARGETING_SSOT"
_ENV_ALLOW_DEFAULT_TARGETING_PATHS = "APPS_RG_ALLOW_DEFAULT_TARGETING_PATHS"
_PREFLIGHT_RECEIPT_FILENAME = "apps_rg_pre_dispatch_preflight.json"
_SCHEMA = "apps_rg.pre_dispatch_preflight.v1"


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def targeting_override_allowed() -> bool:
    """Dev/test waiver for stale DEFAULT_SSOT content or explicit default file paths."""
    return _truthy_env(_ENV_ALLOW_STALE_TARGETING_SSOT) or _truthy_env(
        _ENV_ALLOW_DEFAULT_TARGETING_PATHS
    )


def _resolved_default_path(path: Path, default: Path) -> bool:
    try:
        return path.resolve() == default.resolve()
    except OSError:
        return False


def _read_local_file_body(ref: str) -> tuple[str | None, Path | None, str | None]:
    """Return (body, resolved_path, error)."""
    p = Path(ref)
    if not p.is_file():
        return None, None, f"path does not exist or is not a file: {ref!r}"
    try:
        body = p.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return None, p, f"cannot read file: {exc}"
    return body, p.resolve(), None


def evaluate_jd_cli_input(jd_raw: str) -> tuple[TargetingInputStatus, str]:
    """Classify ``--jd`` before dispatch (path, inline text, or https URI)."""
    ref = str(jd_raw or "").strip()
    if not ref:
        return "MISSING", ""

    if ref.startswith(("http://", "https://")):
        return "PASS", ref

    p = Path(ref)
    if p.is_file():
        if not targeting_override_allowed() and _resolved_default_path(p, DEFAULT_JD_TARGETING_PATH):
            return "DEFAULT_BLOCKED", str(p.resolve())
        body, resolved, err = _read_local_file_body(ref)
        if err:
            return "MISSING", str(resolved or ref)
        if not body:
            return "EMPTY", str(resolved or ref)
        if (
            not targeting_override_allowed()
            and is_stale_default_targeting_jd(body)
        ):
            return "STALE", str(resolved or ref)
        return "PASS", str(resolved or ref)

    if _jd_looks_like_path(ref):
        return "MISSING", ref

    if (
        not targeting_override_allowed()
        and is_stale_default_targeting_jd(ref)
    ):
        return "STALE", "inline:jd"
    return "PASS", "inline:jd"


def evaluate_manual_brief_cli_input(brief_raw: str) -> tuple[TargetingInputStatus, str]:
    """Classify ``--manual-brief`` before dispatch."""
    ref = str(brief_raw or "").strip()
    if not ref:
        return "MISSING", ""

    if ref.startswith(("http://", "https://")):
        return "PASS", ref

    p = Path(ref)
    if p.is_file():
        if not targeting_override_allowed() and _resolved_default_path(
            p, DEFAULT_TARGETING_BRIEFING_PATH
        ):
            return "DEFAULT_BLOCKED", str(p.resolve())
        body, resolved, err = _read_local_file_body(ref)
        if err:
            return "MISSING", str(resolved or ref)
        if not body:
            return "EMPTY", str(resolved or ref)
        if not targeting_override_allowed() and is_stale_default_targeting_briefing(body):
            return "STALE", str(resolved or ref)
        return "PASS", str(resolved or ref)

    if _briefing_looks_like_path(ref):
        return "MISSING", ref

    if not targeting_override_allowed() and is_stale_default_targeting_briefing(ref):
        return "STALE", "inline:manual_brief"
    return "PASS", "inline:manual_brief"


def evaluate_qwen_readiness(
    *,
    lane_provider: str,
    docker_restart_audit: dict[str, Any] | None = None,
) -> tuple[QwenGateStatus, QwenGateStatus, str | None]:
    """Return ``(qwen_health_status, qwen_model_ready_status, detail)``."""
    from apps_rg.runtime.section_cli_preflight import (
        _docker_container_running,
        _http_models_health_check,
        _qwen_container_name,
        should_skip_qwen_vllm_health_gate,
    )

    prov = str(lane_provider or "").strip().lower()
    if prov != "qwen_vllm":
        return "NOT_APPLICABLE", "NOT_APPLICABLE", None

    if should_skip_qwen_vllm_health_gate():
        return "SKIPPED", "SKIPPED", None

    audit = dict(docker_restart_audit or {})
    if audit.get("performed") and not audit.get("ready"):
        detail = str(
            audit.get("probe_error") or audit.get("decisive_reason") or "readiness_probe_failed"
        )
        return "FAIL", "FAIL", detail
    if audit.get("restart_requested") and audit.get("reason") == "model_readiness_failed":
        detail = str(
            audit.get("decisive_reason") or audit.get("readiness_status") or "model_readiness_failed"
        )
        return "FAIL", "FAIL", detail

    container = _qwen_container_name()
    ok_docker, docker_err = _docker_container_running(container)
    if not ok_docker:
        return "FAIL", "NOT_APPLICABLE", f"docker:{docker_err}"

    ok_http, http_err = _http_models_health_check()
    if not ok_http:
        err_lower = (http_err or "").lower()
        if "model" in err_lower or "wrong_or_missing" in err_lower:
            return "PASS", "FAIL", http_err
        return "FAIL", "FAIL", http_err

    return "PASS", "PASS", None


@dataclass(frozen=True, slots=True)
class PreDispatchPreflightResult:
    section: str
    jd_path: str
    jd_status: TargetingInputStatus
    manual_brief_path: str
    manual_brief_status: TargetingInputStatus
    provider_resolution_source: str
    lane_provider: str
    qwen_health_status: QwenGateStatus
    qwen_model_ready_status: QwenGateStatus
    upstream_bullets_status: UpstreamBulletsGateStatus
    upstream_bullets_lane: str
    upstream_bullets_detail: str
    dispatch_started: bool
    decisive_reason: str

    @property
    def allowed(self) -> bool:
        return self.dispatch_started

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": _SCHEMA,
            "recorded_at": time.time(),
            "section": self.section,
            "jd_path": self.jd_path,
            "jd_status": self.jd_status,
            "manual_brief_path": self.manual_brief_path,
            "manual_brief_status": self.manual_brief_status,
            "provider_resolution_source": self.provider_resolution_source,
            "lane_provider": self.lane_provider,
            "qwen_health_status": self.qwen_health_status,
            "qwen_model_ready_status": self.qwen_model_ready_status,
            "upstream_bullets_status": self.upstream_bullets_status,
            "upstream_bullets_lane": self.upstream_bullets_lane,
            "upstream_bullets_detail": self.upstream_bullets_detail,
            "dispatch_started": self.dispatch_started,
            "decisive_reason": self.decisive_reason,
        }


def _targeting_failure_message(
    *,
    jd_status: TargetingInputStatus,
    jd_path: str,
    brief_status: TargetingInputStatus,
    brief_path: str,
) -> str | None:
    parts: list[str] = []
    if jd_status == "MISSING":
        parts.append("--jd is required (file path, https URL, or non-empty inline text).")
    elif jd_status == "EMPTY":
        parts.append(f"--jd file is empty: {jd_path}")
    elif jd_status == "DEFAULT_BLOCKED":
        parts.append(
            f"--jd points at DEFAULT_SSOT placeholder file without override: {jd_path}. "
            f"Pass run-specific JD material or set {_ENV_ALLOW_STALE_TARGETING_SSOT}=1 "
            f"(dev/test only)."
        )
    elif jd_status == "STALE":
        parts.append(
            "JD still matches apps_rg/config/default_jd_targeting.txt (DEFAULT_SSOT placeholder). "
            "Update job description material or pass a run-specific --jd path/text."
        )

    if brief_status == "MISSING":
        parts.append(
            "--manual-brief is required (file path, https URL, or non-empty inline text)."
        )
    elif brief_status == "EMPTY":
        parts.append(f"--manual-brief file is empty: {brief_path}")
    elif brief_status == "DEFAULT_BLOCKED":
        parts.append(
            f"--manual-brief points at DEFAULT_SSOT placeholder file without override: "
            f"{brief_path}. Pass run-specific briefing or set {_ENV_ALLOW_STALE_TARGETING_SSOT}=1 "
            f"(dev/test only)."
        )
    elif brief_status == "STALE":
        parts.append(
            "briefing still matches apps_rg/config/default_targeting_briefing.txt "
            "(DEFAULT_SSOT placeholder). Update briefing material or pass run-specific "
            "--manual-brief path/URL/text."
        )

    if not parts:
        return None
    waiver = (
        f"Override (dev/test): {_ENV_ALLOW_STALE_TARGETING_SSOT}=1 or "
        f"{_ENV_ALLOW_DEFAULT_TARGETING_PATHS}=1."
    )
    return "Pre-dispatch targeting gate blocked: " + " ".join(parts) + " " + waiver


def _qwen_failure_message(
    *,
    health: QwenGateStatus,
    model_ready: QwenGateStatus,
    detail: str | None,
) -> str | None:
    if health == "NOT_APPLICABLE" or health == "SKIPPED":
        return None
    if health == "PASS" and model_ready == "PASS":
        return None
    base = "Pre-dispatch Qwen/vLLM readiness gate blocked"
    if model_ready == "FAIL" and health == "PASS":
        return (
            f"{base}: HTTP /v1/models probe succeeded but expected Qwen model id substring "
            f"was not found. {detail or ''}".strip()
        )
    return f"{base}: {detail or 'qwen_vllm_unavailable'}".strip()


def _upstream_bullets_failure_message(
    *,
    status: UpstreamBulletsGateStatus,
    upstream_lane: str,
    detail: str,
) -> str | None:
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER,
    )

    if status != "BLOCKED":
        return None
    lane = str(upstream_lane or "companion_bullets").strip()
    extra = str(detail or "").strip()
    msg = (
        f"Pre-dispatch companion gate blocked ({PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER}): "
        f"--section {lane} must be ACCEPTED_FINALIZED (REAL_LLM, product_quality PASS, "
        f"X3 allow-family) before narrative dispatch."
    )
    if extra:
        msg = f"{msg} ({extra})"
    return msg


def run_pre_dispatch_preflight(
    *,
    section: str,
    jd: str,
    manual_brief: str,
    lane_provider: str,
    provider_resolution_source: str,
    docker_restart_audit: dict[str, Any] | None = None,
) -> PreDispatchPreflightResult:
    """Evaluate all mandatory gates; ``dispatch_started`` is False when any gate fails."""
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        evaluate_narrative_upstream_bullets_gate,
    )

    jd_status, jd_path = evaluate_jd_cli_input(jd)
    brief_status, brief_path = evaluate_manual_brief_cli_input(manual_brief)
    q_health, q_model, q_detail = evaluate_qwen_readiness(
        lane_provider=lane_provider,
        docker_restart_audit=docker_restart_audit,
    )
    upstream_status, upstream_lane, upstream_detail = evaluate_narrative_upstream_bullets_gate(
        str(section).strip()
    )

    decisive = ""
    dispatch_started = True

    targeting_err = _targeting_failure_message(
        jd_status=jd_status,
        jd_path=jd_path,
        brief_status=brief_status,
        brief_path=brief_path,
    )
    if targeting_err:
        decisive = targeting_err
        dispatch_started = False
    else:
        upstream_err = _upstream_bullets_failure_message(
            status=upstream_status,
            upstream_lane=upstream_lane,
            detail=upstream_detail,
        )
        if upstream_err:
            decisive = upstream_err
            dispatch_started = False
        else:
            qwen_err = _qwen_failure_message(
                health=q_health,
                model_ready=q_model,
                detail=q_detail,
            )
            if qwen_err:
                decisive = qwen_err
                dispatch_started = False
            else:
                decisive = "all_pre_dispatch_gates_passed"

    return PreDispatchPreflightResult(
        section=str(section).strip(),
        jd_path=jd_path,
        jd_status=jd_status,
        manual_brief_path=brief_path,
        manual_brief_status=brief_status,
        provider_resolution_source=str(provider_resolution_source),
        lane_provider=str(lane_provider),
        qwen_health_status=q_health,
        qwen_model_ready_status=q_model,
        upstream_bullets_status=upstream_status,
        upstream_bullets_lane=upstream_lane,
        upstream_bullets_detail=upstream_detail,
        dispatch_started=dispatch_started,
        decisive_reason=decisive,
    )


def resolve_preflight_receipt_path(*, artifact_dir: str, section: str) -> Path:
    """Choose receipt directory: explicit artifact dir, else repo preflight bucket."""
    ad = str(artifact_dir or "").strip()
    if ad:
        out = Path(ad)
        out.mkdir(parents=True, exist_ok=True)
        return out / _PREFLIGHT_RECEIPT_FILENAME
    root = find_repo_root()
    bucket = root / "artifacts" / "apps_rg" / "preflight_receipts"
    bucket.mkdir(parents=True, exist_ok=True)
    safe_section = str(section or "unknown").strip().replace("/", "_") or "unknown"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    return bucket / f"pre_dispatch_{safe_section}_{stamp}.json"


def write_pre_dispatch_preflight_receipt(
    path: Path,
    result: PreDispatchPreflightResult,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def enforce_pre_dispatch_preflight(
    *,
    section: str,
    jd: str,
    manual_brief: str,
    lane_provider: str,
    provider_resolution_source: str,
    artifact_dir: str = "",
    docker_restart_audit: dict[str, Any] | None = None,
) -> PreDispatchPreflightResult:
    """Run gates, persist receipt, raise ``SectionCliConfigError`` when blocked."""
    from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

    result = run_pre_dispatch_preflight(
        section=section,
        jd=jd,
        manual_brief=manual_brief,
        lane_provider=lane_provider,
        provider_resolution_source=provider_resolution_source,
        docker_restart_audit=docker_restart_audit,
    )
    receipt_path = resolve_preflight_receipt_path(artifact_dir=artifact_dir, section=section)
    write_pre_dispatch_preflight_receipt(receipt_path, result)
    if not result.allowed:
        raise SectionCliConfigError(result.decisive_reason)
    return result


__all__ = [
    "PreDispatchPreflightResult",
    "TargetingInputStatus",
    "QwenGateStatus",
    "UpstreamBulletsGateStatus",
    "enforce_pre_dispatch_preflight",
    "evaluate_jd_cli_input",
    "evaluate_manual_brief_cli_input",
    "evaluate_qwen_readiness",
    "run_pre_dispatch_preflight",
    "resolve_preflight_receipt_path",
    "targeting_override_allowed",
    "write_pre_dispatch_preflight_receipt",
]
