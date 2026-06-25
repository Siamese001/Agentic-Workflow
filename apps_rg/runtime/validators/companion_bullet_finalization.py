"""Shared rules for upstream bullet lanes feeding narrative companion context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, Mapping

from apps_rg.runtime.section_execution_plan import (
    HARD_NO_RETRY_RUNTIME_STATUSES,
    is_hard_no_retry_runtime_status,
)

ACCEPTED_FINALIZED_COMPANION_STATUS = "ACCEPTED_FINALIZED"
UpstreamBulletsGateStatus = Literal["NOT_APPLICABLE", "PASS", "BLOCKED"]
UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS = "BLOCKED_UPSTREAM_NOT_FINALIZED"
PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER = "UPSTREAM_BULLETS_NOT_FINALIZED"

# Failure classes that retries cannot fix. Per the variance-class mental model: SC fixes
# generation variance, more judges fix evaluation variance, deterministic gates fix mechanical
# rules, and UPSTREAM FIXES fix missing evidence. When a section reports one of these, the
# upstream state is unchanged on a re-run with the same inputs — so the best-of-N retry loop
# must EARLY-EXIT (break) instead of paying preflight again for a guaranteed-fail. Dependent
# downstream sections (narratives -> exec_summary -> headline) skip via the dependency order.
UPSTREAM_BLOCKED_RUNTIME_STATUSES: frozenset[str] = HARD_NO_RETRY_RUNTIME_STATUSES

# Upstream bullets may proceed to narrative when L2+X2 product proof passed but a judge provider blocked.
COMPANION_FINALIZED_X3_CODES: frozenset[str] = frozenset(
    {
        "X3_ALLOW",
        "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        # Deterministic X2/product_quality passed; judge soft-fail must not block narrative LLM.
        "X3_REVIEW_JUDGE_SOFT_FAIL",
    }
)

_PROVIDER_UNAVAILABLE_ERROR_TOKENS: tuple[str, ...] = (
    "api usage limits",
    "provider_unavailable",
    "provider unavailable",
    "quota",
    "rate limit",
    "rate_limit",
    "usage limit",
)


def companion_allow_legacy_stale_fallback() -> bool:
    """Legacy stale companion fallback is disabled for all paths."""
    return False


def companion_blocks_narrative_llm(companion_context: Mapping[str, Any]) -> bool:
    """True when narrative must not call the provider (product fail-closed)."""
    if companion_allow_legacy_stale_fallback():
        return False
    return str(companion_context.get("status") or "") != ACCEPTED_FINALIZED_COMPANION_STATUS


def evaluate_companion_bullet_lane_finalized(
    *,
    upstream_section_id: str,
    l2_data: dict[str, Any],
    x3_code: str,
    expected_bullet_ids: tuple[str, ...],
    x3_data: Mapping[str, Any] | None = None,
    x1d_data: Mapping[str, Any] | None = None,
) -> tuple[str, str]:
    """Return (ACCEPTED_FINALIZED|PENDING|NOT_FINALIZED, reason)."""
    reasons: list[str] = []
    if str(l2_data.get("section_id") or "") != upstream_section_id:
        reasons.append(f"section_id_not_{upstream_section_id}")
    bullet_ids = [str(b.get("bullet_id")) for b in (l2_data.get("bullets") or []) if isinstance(b, dict)]
    if bullet_ids != list(expected_bullet_ids):
        reasons.append("bullet_ids_mismatch")
    if str(l2_data.get("product_quality_status") or "") != "PASS":
        reasons.append(f"product_quality_not_PASS:{l2_data.get('product_quality_status')}")
    if str(l2_data.get("runtime_generation_status") or "") != "REAL_LLM":
        reasons.append(f"runtime_not_REAL_LLM:{l2_data.get('runtime_generation_status')}")
    if x3_code not in COMPANION_FINALIZED_X3_CODES and not _is_provider_unavailable_x3_block(
        x3_code=x3_code,
        x3_data=x3_data,
        x1d_data=x1d_data,
    ):
        reasons.append(f"x3_not_companion_finalized:{x3_code}")
    if reasons:
        return "NOT_FINALIZED", ";".join(reasons)
    return ACCEPTED_FINALIZED_COMPANION_STATUS, "ok"


def _is_provider_unavailable_x3_block(
    *,
    x3_code: str,
    x3_data: Mapping[str, Any] | None,
    x1d_data: Mapping[str, Any] | None,
) -> bool:
    """Treat quota/provider transport X3_BLOCK as finalized for narrative synthesis.

    The companion narrative depends on deterministic bullet quality, not release
    authorization. This exception is intentionally narrow: X2/product failures and
    genuine judge verdict failures remain blocked.
    """
    if str(x3_code or "") != "X3_BLOCK":
        return False
    x3 = x3_data or {}
    if str(x3.get("product_quality_status") or "") != "PASS":
        return False
    if x3.get("x2_failed_gates") or x3.get("mocked_judges"):
        return False
    decisive = x3.get("decisive_judge_failures") or []
    if not isinstance(decisive, list) or not decisive:
        return False
    judges = (x1d_data or {}).get("judges") or []
    if not isinstance(judges, list) or not judges:
        return False
    decisive_keys = {str(item) for item in decisive}
    matching_errors: list[str] = []
    for row in judges:
        if not isinstance(row, Mapping):
            continue
        key = str(row.get("provider_key") or "")
        if key not in decisive_keys:
            continue
        err = str(row.get("exact_provider_error") or row.get("error") or "").lower()
        status = str(row.get("provider_status") or "").lower()
        if err and any(token in err for token in _PROVIDER_UNAVAILABLE_ERROR_TOKENS):
            matching_errors.append(err)
        elif "blocked" in status or "unavailable" in status:
            matching_errors.append(status)
    return bool(matching_errors) and len(matching_errors) == len(decisive_keys)


def companion_run_dir_accepted(run_dir: Any, *, upstream_section_id: str, expected_bullet_ids: tuple[str, ...]) -> bool:
    """True when run_dir contains accepted upstream bullet evidence."""
    rd = Path(run_dir)
    l2_path = rd / "l2_output.json"
    x3_path = rd / "x3_disposition.json"
    if not l2_path.is_file():
        return False
    try:
        l2 = json.loads(l2_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    x3_code = "UNKNOWN"
    x3_data: dict[str, Any] | None = None
    if x3_path.is_file():
        try:
            x3_data = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3_data.get("x3_code") or x3_data.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            return False
    x1d_data: dict[str, Any] | None = None
    x1d_path = rd / "x1d_llm_judge_outputs.json"
    if x1d_path.is_file():
        try:
            x1d_data = json.loads(x1d_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
    status, _reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id=upstream_section_id,
        l2_data=l2,
        x3_code=x3_code,
        expected_bullet_ids=expected_bullet_ids,
        x3_data=x3_data,
        x1d_data=x1d_data,
    )
    return status == ACCEPTED_FINALIZED_COMPANION_STATUS


def _l2_from_modular_successful_pointer(repo: Path, upstream_section_id: str) -> Path | None:
    from apps_rg.runtime.runtime_proof_layout import (
        LATEST_SUCCESSFUL_REAL_FILENAME,
        _read_json_dict,
        modular_sections_root_from_env,
    )

    msr = modular_sections_root_from_env(repo)
    if msr is None:
        return None
    ptr = msr / upstream_section_id / LATEST_SUCCESSFUL_REAL_FILENAME
    data = _read_json_dict(ptr)
    if not data:
        return None
    rel = data.get("run_dir")
    if not isinstance(rel, str) or not rel.strip():
        return None
    rd = (repo / rel).resolve()
    l2 = rd / "l2_output.json"
    return l2 if l2.is_file() else None


def _l2_from_legacy_stale_fallback(
    repo: Path,
    upstream_section_id: str,
    *,
    expected_bullet_ids: tuple[str, ...],
) -> Path | None:
    """Legacy global scan is disabled; current-run modular evidence is required."""
    _ = (repo, upstream_section_id, expected_bullet_ids)
    return None


def resolve_companion_bullets_l2_path(
    repo: Path,
    *,
    upstream_section_id: str,
    expected_bullet_ids: tuple[str, ...],
) -> Path | None:
    """Resolve upstream bullet L2 for narrative companion context.

    Product and test paths: modular ``latest_successful_real_run.json`` only
    from the current run tree. Global runtime_proofs scans are forbidden.
    """
    modular_l2 = _l2_from_modular_successful_pointer(repo, upstream_section_id)
    if modular_l2 is not None:
        if companion_run_dir_accepted(
            modular_l2.parent,
            upstream_section_id=upstream_section_id,
            expected_bullet_ids=expected_bullet_ids,
        ):
            return modular_l2
        return None
    return None


def companion_accepted_in_modular_sections_root(
    repo: Path,
    sections_root: Path,
    *,
    upstream_section_id: str,
    expected_bullet_ids: tuple[str, ...],
) -> bool:
    """True when the current modular run has accepted upstream bullets (no global fallback)."""
    from apps_rg.runtime.runtime_proof_layout import LATEST_SUCCESSFUL_REAL_FILENAME, _read_json_dict

    ptr = Path(sections_root) / upstream_section_id / LATEST_SUCCESSFUL_REAL_FILENAME
    data = _read_json_dict(ptr)
    if not data:
        return False
    rel = data.get("run_dir")
    if not isinstance(rel, str) or not rel.strip():
        return False
    rd = (repo / rel).resolve()
    return companion_run_dir_accepted(
        rd,
        upstream_section_id=upstream_section_id,
        expected_bullet_ids=expected_bullet_ids,
    )


def build_companion_bullets_context(
    repo: Path,
    *,
    upstream_section_id: str,
    expected_bullet_ids: tuple[str, ...],
) -> dict[str, Any]:
    """Build companion status + read-only bullet text for narrative lanes."""
    missing_reason = f"{upstream_section_id}_l2_output_not_found"
    base: dict[str, Any] = {
        "status": "MISSING",
        "reason": missing_reason,
        "text": "",
        "l2_ref": None,
        "x3_ref": None,
        "bullet_ids": [],
        "product_quality_status": "UNKNOWN",
        "x3_code": "UNKNOWN",
    }
    path = resolve_companion_bullets_l2_path(
        repo,
        upstream_section_id=upstream_section_id,
        expected_bullet_ids=expected_bullet_ids,
    )
    if path is None or not path.is_file():
        if not companion_allow_legacy_stale_fallback():
            base["reason"] = f"{missing_reason}:no_modular_accepted_upstream_in_current_run"
        return base
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            **base,
            "status": "INVALID",
            "reason": f"{upstream_section_id}_l2_unreadable:{type(exc).__name__}",
            "l2_ref": str(path),
        }

    bullets = data.get("bullets") or []
    bullet_ids = [str(b.get("bullet_id")) for b in bullets if isinstance(b, dict)]
    text = "\n".join(
        f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}" for b in bullets if isinstance(b, dict)
    )
    product_quality_status = str(data.get("product_quality_status") or "UNKNOWN")
    x3_path = path.parent / "x3_disposition.json"
    x3_code = "UNKNOWN"
    x3_data: dict[str, Any] | None = None
    if x3_path.is_file():
        try:
            x3_data = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3_data.get("x3_code") or x3_data.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            x3_code = "UNREADABLE"
    x1d_path = path.parent / "x1d_llm_judge_outputs.json"
    x1d_data: dict[str, Any] | None = None
    if x1d_path.is_file():
        try:
            x1d_data = json.loads(x1d_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            x1d_data = None

    status, reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id=upstream_section_id,
        l2_data=data,
        x3_code=x3_code,
        expected_bullet_ids=expected_bullet_ids,
        x3_data=x3_data,
        x1d_data=x1d_data,
    )
    rel_l2 = str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path)
    x3_ref_val: str | None = None
    if x3_path.is_file():
        x3_ref_val = str(x3_path.relative_to(repo)) if x3_path.is_relative_to(repo) else str(x3_path)

    return {
        "status": status,
        "reason": reason,
        "text": text,
        "l2_ref": rel_l2,
        "x3_ref": x3_ref_val,
        "bullet_ids": bullet_ids,
        "product_quality_status": product_quality_status,
        "x3_code": x3_code,
    }


def _narrative_upstream_spec(narrative_section_id: str) -> tuple[str, tuple[str, ...]] | None:
    from apps_rg.runtime.reasoning.employment_bullet_pool import REQUIRED_BULLET_IDS
    from apps_rg.runtime.section_execution_plan import NARRATIVE_UPSTREAM_BULLET_LANE

    sid = str(narrative_section_id).strip()
    upstream = NARRATIVE_UPSTREAM_BULLET_LANE.get(sid)
    if not upstream:
        return None
    return upstream, tuple(REQUIRED_BULLET_IDS.get(upstream, ()))


def evaluate_narrative_upstream_bullets_gate(
    narrative_section_id: str,
    *,
    repo: Path | None = None,
) -> tuple[UpstreamBulletsGateStatus, str, str]:
    """Pre-dispatch gate: narrative lanes require finalized companion bullet evidence."""
    spec = _narrative_upstream_spec(narrative_section_id)
    if spec is None:
        return "NOT_APPLICABLE", "", ""

    upstream_lane, expected_ids = spec
    from apps_rg.runtime.runtime_proof_layout import (
        find_repo_root,
        modular_sections_root_from_env,
    )

    root = repo if repo is not None else find_repo_root()
    msr = modular_sections_root_from_env(root)
    if msr is not None:
        if companion_accepted_in_modular_sections_root(
            root,
            msr,
            upstream_section_id=upstream_lane,
            expected_bullet_ids=expected_ids,
        ):
            return "PASS", upstream_lane, "modular_accepted"
        return (
            "BLOCKED",
            upstream_lane,
            f"{upstream_lane} not ACCEPTED_FINALIZED in current modular sections root",
        )

    return (
        "BLOCKED",
        upstream_lane,
        f"current modular sections root missing; run {upstream_lane} in the same e2e run before "
        f"{narrative_section_id}",
    )


def is_upstream_blocked_runtime_status(runtime_generation_status: str | None) -> bool:
    """True when a section's runtime_generation_status is a non-retryable upstream block."""
    return is_hard_no_retry_runtime_status(runtime_generation_status)


__all__ = [
    "ACCEPTED_FINALIZED_COMPANION_STATUS",
    "COMPANION_FINALIZED_X3_CODES",
    "PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER",
    "UPSTREAM_BLOCKED_RUNTIME_STATUSES",
    "UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS",
    "is_upstream_blocked_runtime_status",
    "build_companion_bullets_context",
    "companion_accepted_in_modular_sections_root",
    "companion_allow_legacy_stale_fallback",
    "companion_blocks_narrative_llm",
    "companion_run_dir_accepted",
    "evaluate_companion_bullet_lane_finalized",
    "evaluate_narrative_upstream_bullets_gate",
    "resolve_companion_bullets_l2_path",
    "UpstreamBulletsGateStatus",
]
