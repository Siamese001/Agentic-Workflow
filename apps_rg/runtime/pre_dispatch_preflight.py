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

from apps_rg.prerequisites.briefing_validator import (
    AppsResearchHandoffValidation,
    validate_apps_research_handoff,
)
from apps_rg.runtime.briefing_resolution import _looks_like_filesystem_ref as _briefing_looks_like_path
from apps_rg.runtime.briefing_ssot import DEFAULT_TARGETING_BRIEFING_PATH
from apps_rg.runtime.jd_resolution import DEFAULT_JD_TARGETING_PATH, _looks_like_filesystem_ref as _jd_looks_like_path
from apps_rg.runtime.runtime_proof_layout import find_repo_root
from apps_rg.runtime.targeting_input_freshness import (
    is_stale_default_targeting_briefing,
    is_stale_default_targeting_jd,
)

TargetingInputStatus = Literal["PASS", "MISSING", "EMPTY", "STALE", "DEFAULT_BLOCKED"]
ProviderGateStatus = Literal["PASS", "FAIL", "SKIPPED", "NOT_APPLICABLE"]
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


def evaluate_provider_readiness(
    *,
    lane_provider: str,
    docker_restart_audit: dict[str, Any] | None = None,
) -> tuple[ProviderGateStatus, ProviderGateStatus, str | None]:
    """Local-provider readiness gate removed with the local-model provider.

    The external generation provider owns its own transport and surfaces a BLOCKED
    ``ProviderResult`` on failure, so there is no pre-dispatch local-container readiness
    check. Always ``NOT_APPLICABLE``.
    """
    return "NOT_APPLICABLE", "NOT_APPLICABLE", None


@dataclass(frozen=True, slots=True)
class PreDispatchPreflightResult:
    section: str
    jd_path: str
    jd_status: TargetingInputStatus
    manual_brief_path: str
    manual_brief_status: TargetingInputStatus
    provider_resolution_source: str
    lane_provider: str
    provider_health_status: ProviderGateStatus
    provider_model_ready_status: ProviderGateStatus
    upstream_bullets_status: UpstreamBulletsGateStatus
    upstream_bullets_lane: str
    upstream_bullets_detail: str
    dispatch_started: bool
    decisive_reason: str
    apps_research_handoff_validation: dict[str, Any] | None = None
    apps_research_briefing_envelope: dict[str, Any] | None = None

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
            "provider_health_status": self.provider_health_status,
            "provider_model_ready_status": self.provider_model_ready_status,
            "upstream_bullets_status": self.upstream_bullets_status,
            "upstream_bullets_lane": self.upstream_bullets_lane,
            "upstream_bullets_detail": self.upstream_bullets_detail,
            "dispatch_started": self.dispatch_started,
            "decisive_reason": self.decisive_reason,
            "apps_research_handoff_validation": self.apps_research_handoff_validation,
            "apps_research_briefing_envelope": self.apps_research_briefing_envelope,
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


def _apps_research_handoff_failure_message(
    validation: AppsResearchHandoffValidation,
) -> str | None:
    if validation.valid:
        return None
    return (
        "Pre-dispatch apps_research handoff gate blocked: "
        f"{validation.reason}. Refresh apps_research or pass a valid non-stale briefing."
    )


def _provider_failure_message(
    *,
    health: ProviderGateStatus,
    model_ready: ProviderGateStatus,
    detail: str | None,
) -> str | None:
    if health == "NOT_APPLICABLE" or health == "SKIPPED":
        return None
    if health == "PASS" and model_ready == "PASS":
        return None
    base = "Pre-dispatch provider readiness gate blocked"
    if model_ready == "FAIL" and health == "PASS":
        return (
            f"{base}: provider probe succeeded but expected model identifier was not found. "
            f"{detail or ''}".strip()
        )
    return f"{base}: {detail or 'provider_unavailable'}".strip()


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
        f"with no deterministic X2 failures; provider-quota judge blocks are non-release proof only) "
        f"before narrative dispatch."
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
    require_apps_research_handoff: bool = False,
    require_apps_research_x1_x3: bool = False,
) -> PreDispatchPreflightResult:
    """Evaluate all mandatory gates; ``dispatch_started`` is False when any gate fails."""
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        evaluate_narrative_upstream_bullets_gate,
    )

    jd_status, jd_path = evaluate_jd_cli_input(jd)
    brief_status, brief_path = evaluate_manual_brief_cli_input(manual_brief)
    handoff_validation = validate_apps_research_handoff(
        brief_ref=manual_brief,
        jd_ref=jd,
        require_observed=require_apps_research_handoff,
        require_x1_x3_authorization=require_apps_research_x1_x3,
    )
    provider_health, provider_model, provider_detail = evaluate_provider_readiness(
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
        handoff_err = _apps_research_handoff_failure_message(handoff_validation)
        if handoff_err:
            decisive = handoff_err
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
                provider_err = _provider_failure_message(
                    health=provider_health,
                    model_ready=provider_model,
                    detail=provider_detail,
                )
                if provider_err:
                    decisive = provider_err
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
        provider_health_status=provider_health,
        provider_model_ready_status=provider_model,
        upstream_bullets_status=upstream_status,
        upstream_bullets_lane=upstream_lane,
        upstream_bullets_detail=upstream_detail,
        dispatch_started=dispatch_started,
        decisive_reason=decisive,
        apps_research_handoff_validation=(
            handoff_validation.to_receipt()
            if handoff_validation.observed or not handoff_validation.valid
            else None
        ),
        apps_research_briefing_envelope=handoff_validation.envelope,
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
    if result.apps_research_handoff_validation:
        (path.parent / "apps_research_handoff_validation_receipt.json").write_text(
            json.dumps(result.apps_research_handoff_validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if result.apps_research_briefing_envelope:
        (path.parent / "apps_research_briefing_envelope.json").write_text(
            json.dumps(result.apps_research_briefing_envelope, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
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
    require_apps_research_handoff: bool = False,
    require_apps_research_x1_x3: bool = False,
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
        require_apps_research_handoff=require_apps_research_handoff,
        require_apps_research_x1_x3=require_apps_research_x1_x3,
    )
    receipt_path = resolve_preflight_receipt_path(artifact_dir=artifact_dir, section=section)
    write_pre_dispatch_preflight_receipt(receipt_path, result)
    if not result.allowed:
        raise SectionCliConfigError(result.decisive_reason)
    return result


__all__ = [
    "PreDispatchPreflightResult",
    "TargetingInputStatus",
    "ProviderGateStatus",
    "UpstreamBulletsGateStatus",
    "enforce_pre_dispatch_preflight",
    "evaluate_jd_cli_input",
    "evaluate_manual_brief_cli_input",
    "evaluate_provider_readiness",
    "run_pre_dispatch_preflight",
    "resolve_preflight_receipt_path",
    "targeting_override_allowed",
    "write_pre_dispatch_preflight_receipt",
]
