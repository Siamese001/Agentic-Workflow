"""W5 coherent rollup policy — digest/proof compatibility and same-run policy."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.aggregation.preflight import run_aggregation_preflight
from apps_rg.runtime.aggregation.run_fingerprint import build_fingerprint_from_rollup
from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS

POLICY_SCHEMA = "apps_rg.coherent_rollup_policy.v1"

# Structural assembly only proceeds when the current session's lanes are coherent.
# Mixed-date pin reuse used to be accepted under coherent_aggregation_pin; that is now
# blocked so stale per-lane pins cannot be stitched into a fresh full-run assembly.


def _collect_proof_pool_fields(sealed_index: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    digests: dict[str, str] = {}
    refs: dict[str, str] = {}
    for ptr in sealed_index.get("pointers") or []:
        if not isinstance(ptr, dict):
            continue
        lane = str(ptr.get("lane") or "")
        dig = ptr.get("proof_pool_digest")
        ref = ptr.get("proof_pool_ref")
        if lane and isinstance(dig, str) and dig.strip():
            digests[lane] = dig
        if lane and isinstance(ref, str) and ref.strip():
            refs[lane] = ref.replace("\\", "/")
    return digests, refs


def evaluate_coherent_rollup_policy(
    *,
    repo: Path,
    rollup_blob: dict[str, Any],
    base_resume_digest: str,
) -> dict[str, Any]:
    fingerprint, sealed_index = build_fingerprint_from_rollup(
        repo=repo,
        rollup_blob=rollup_blob,
        base_resume_digest=base_resume_digest,
    )
    preflight = run_aggregation_preflight(
        repo=repo,
        rollup_blob=rollup_blob,
        fingerprint=fingerprint,
        sealed_index=sealed_index,
    )
    preflight_pass = all(r.pass_ for r in preflight)

    pool_digests, pool_refs = _collect_proof_pool_fields(sealed_index)
    unique_pool_refs = set(pool_refs.values())
    # Per-lane pool digests differ by SRFS section selection; policy coherence is shared ledger ref.
    pool_policy_coherent = len(unique_pool_refs) <= 1 if unique_pool_refs else True

    same_date = bool(fingerprint.get("same_date_prefix_coherent"))
    pinned = bool(rollup_blob.get("coherent_aggregation_pin"))
    if same_date:
        same_run_reason = "all lane run_id date prefixes match"
        structural_ok = preflight_pass
    elif pinned:
        same_run_reason = (
            "mixed run_id date prefixes are not accepted even under coherent_aggregation_pin — "
            "require a single current-run session"
        )
        structural_ok = False
    else:
        same_run_reason = (
            "mixed run_id date prefixes without coherent pin are not accepted — require a "
            "single current-run session"
        )
        structural_ok = False

    lane_matrix: list[dict[str, Any]] = []
    for lane in GENERATED_LANE_IDS:
        ptr = next((p for p in (sealed_index.get("pointers") or []) if p.get("lane") == lane), {})
        lane_matrix.append(
            {
                "lane": lane,
                "run_id": ptr.get("run_id"),
                "x3_code": ptr.get("x3_code"),
                "pool_receipt_status": ptr.get("pool_receipt_status"),
                "proof_pool_digest": ptr.get("proof_pool_digest"),
                "jd_digest": ptr.get("jd_digest"),
                "briefing_digest": ptr.get("briefing_digest"),
                "x2_failed": (ptr.get("x2_failed") if isinstance(ptr, dict) else None),
                "product_quality_status": ptr.get("product_quality_status"),
            },
        )

    product_acceptable_pool_reason: str | None = None
    if not pool_policy_coherent and pinned and len(unique_pool_refs) > 1:
        product_acceptable_pool_reason = (
            "Per-lane SRFS proof_pool_ref split (master ledger, exec_summary SRFS slice, base-resume "
            "IBM scope) under coherent_aggregation_pin; mixed-date reuse is blocked for structural "
            "assembly, so only current-run pins are eligible."
        )

    return {
        "schema": POLICY_SCHEMA,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rollup_id": str(rollup_blob.get("rollup_id") or ""),
        "coherent_aggregation_pin": pinned,
        "coherent_run_date_prefix": rollup_blob.get("coherent_run_date_prefix"),
        "product_acceptable_proof_pool_policy_reason": product_acceptable_pool_reason,
        "same_run_policy": {
            "same_run_coherent": fingerprint.get("same_run_coherent"),
            "same_date_prefix_coherent": same_date,
            "acceptable_for_structural_assembly": same_date,
            "coherent_rollup_policy_reason": same_run_reason,
            "require_single_orchestration_pass": not same_date,
        },
        "digest_coherence": {
            "base_resume_digest": base_resume_digest,
            "jd_digest_coherent": fingerprint.get("jd_digest_coherent"),
            "briefing_digest_coherent": fingerprint.get("briefing_digest_coherent"),
            "proof_pool_policy_coherent": pool_policy_coherent,
            "unique_proof_pool_refs": sorted(unique_pool_refs),
            "per_lane_proof_pool_ref": pool_refs,
            "per_lane_proof_pool_digest": pool_digests,
            "note": "Per-lane proof_pool_digest may differ; shared proof_pool_ref is the SRFS policy anchor.",
        },
        "preflight_all_pass": preflight_pass,
        "structural_assembly_eligible": structural_ok and preflight_pass,
        "lane_compatibility_matrix": lane_matrix,
        "orchestration_fingerprint_ref": fingerprint,
    }
