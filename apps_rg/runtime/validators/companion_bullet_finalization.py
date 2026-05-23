"""Shared rules for upstream bullet lanes feeding narrative companion context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ACCEPTED_FINALIZED_COMPANION_STATUS = "ACCEPTED_FINALIZED"
UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS = "BLOCKED_UPSTREAM_NOT_FINALIZED"
PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER = "UPSTREAM_BULLETS_NOT_FINALIZED"

# Upstream bullets may proceed to narrative when L2+X2 product proof passed but a judge provider blocked.
COMPANION_FINALIZED_X3_CODES: frozenset[str] = frozenset(
    {
        "X3_ALLOW",
        "X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        # Deterministic X2/product_quality passed; judge soft-fail must not block narrative LLM.
        "X3_REVIEW_JUDGE_SOFT_FAIL",
    }
)


def companion_allow_legacy_stale_fallback() -> bool:
    """When False, never scan global runtime_proofs for older accepted bullet runs."""
    from apps_rg.runtime.product_output_policy import is_apps_rg_test_harness

    return is_apps_rg_test_harness()


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
    if x3_code not in COMPANION_FINALIZED_X3_CODES:
        reasons.append(f"x3_not_companion_finalized:{x3_code}")
    if reasons:
        return "NOT_FINALIZED", ";".join(reasons)
    return ACCEPTED_FINALIZED_COMPANION_STATUS, "ok"


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
    if x3_path.is_file():
        try:
            x3 = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            return False
    status, _reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id=upstream_section_id,
        l2_data=l2,
        x3_code=x3_code,
        expected_bullet_ids=expected_bullet_ids,
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


def _l2_from_legacy_stale_fallback(repo: Path, upstream_section_id: str, *, expected_bullet_ids: tuple[str, ...]) -> Path | None:
    from apps_rg.runtime.runtime_proof_layout import (
        LATEST_SUCCESSFUL_REAL_FILENAME,
        lane_root,
        resolve_effective_lane_l2_path,
        _read_json_dict,
    )

    path = resolve_effective_lane_l2_path(repo, upstream_section_id)
    if path is not None and path.is_file() and companion_run_dir_accepted(
        path.parent,
        upstream_section_id=upstream_section_id,
        expected_bullet_ids=expected_bullet_ids,
    ):
        return path

    real_lane = lane_root(repo, upstream_section_id) / "real"
    if real_lane.is_dir():
        glob_pat = f"{upstream_section_id}_*"
        for run_dir in sorted(real_lane.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True):
            if companion_run_dir_accepted(
                run_dir,
                upstream_section_id=upstream_section_id,
                expected_bullet_ids=expected_bullet_ids,
            ):
                candidate = run_dir / "l2_output.json"
                if candidate.is_file():
                    return candidate

    succ_ptr = lane_root(repo, upstream_section_id) / LATEST_SUCCESSFUL_REAL_FILENAME
    succ = _read_json_dict(succ_ptr) or {}
    rel = succ.get("l2_output_repo_relative") or succ.get("run_dir")
    if isinstance(rel, str) and rel.strip():
        alt = (repo / rel).resolve()
        alt_l2 = alt / "l2_output.json" if alt.is_dir() else alt
        if alt_l2.is_file() and companion_run_dir_accepted(
            alt_l2.parent,
            upstream_section_id=upstream_section_id,
            expected_bullet_ids=expected_bullet_ids,
        ):
            return alt_l2
    return None


def resolve_companion_bullets_l2_path(
    repo: Path,
    *,
    upstream_section_id: str,
    expected_bullet_ids: tuple[str, ...],
) -> Path | None:
    """Resolve upstream bullet L2 for narrative companion context.

    Product path: modular ``latest_successful_real_run.json`` only (current run tree).
    Test harness may fall back to global runtime_proofs scans.
    """
    modular_l2 = _l2_from_modular_successful_pointer(repo, upstream_section_id)
    if modular_l2 is not None:
        if companion_run_dir_accepted(
            modular_l2.parent,
            upstream_section_id=upstream_section_id,
            expected_bullet_ids=expected_bullet_ids,
        ):
            return modular_l2
        if not companion_allow_legacy_stale_fallback():
            return None
    if not companion_allow_legacy_stale_fallback():
        return None
    return _l2_from_legacy_stale_fallback(repo, upstream_section_id, expected_bullet_ids=expected_bullet_ids)


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
    if x3_path.is_file():
        try:
            x3 = json.loads(x3_path.read_text(encoding="utf-8"))
            x3_code = str(x3.get("x3_code") or x3.get("x3_disposition") or "UNKNOWN")
        except (json.JSONDecodeError, OSError):
            x3_code = "UNREADABLE"

    status, reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id=upstream_section_id,
        l2_data=data,
        x3_code=x3_code,
        expected_bullet_ids=expected_bullet_ids,
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


__all__ = [
    "ACCEPTED_FINALIZED_COMPANION_STATUS",
    "COMPANION_FINALIZED_X3_CODES",
    "PRE_RUN_UPSTREAM_NOT_FINALIZED_BLOCKER",
    "UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS",
    "build_companion_bullets_context",
    "companion_accepted_in_modular_sections_root",
    "companion_allow_legacy_stale_fallback",
    "companion_blocks_narrative_llm",
    "companion_run_dir_accepted",
    "evaluate_companion_bullet_lane_finalized",
    "resolve_companion_bullets_l2_path",
]
