"""W1 aggregation preflight — fail-closed before final resume assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import GENERATED_LANE_IDS
from apps_rg.runtime.aggregation.section_sealed_index import GENERATED_LANE_PROOF_FILES

REQUIRED_PROOF_FILES: tuple[str, ...] = (
    "section_input_usage_ledger.json",
    "x2_source_fact_pool_receipt.json",
    "x2_gate_outputs.json",
    "x3_disposition.json",
    "l2_output.json",
)


class AggregationPreflightError(Exception):
    """Raised when aggregation preflight gates fail (fail-closed)."""

    def __init__(self, failures: list[dict[str, Any]]) -> None:
        self.failures = failures
        msgs = "; ".join(f"{f.get('gate_id')}: {f.get('decisive_reason')}" for f in failures)
        super().__init__(msgs)


@dataclass
class PreflightResult:
    gate_id: str
    pass_: bool
    decisive_reason: str | None = None
    observed: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "pass": self.pass_,
            "decisive_reason": self.decisive_reason,
            "observed": self.observed,
        }


def _is_blocked_x3(code: str) -> bool:
    u = code.upper()
    if u.startswith("X3_BLOCK") or ("BLOCKED" in u and "REVIEW" not in u):
        return True
    return "DENY" in u


def _is_review_x3(code: str) -> bool:
    return "REVIEW" in code.upper()


def _resolved_run_dir(repo: Path, rel: str) -> Path:
    rel_norm = rel.replace("\\", "/")
    while rel_norm.startswith("./"):
        rel_norm = rel_norm[2:]
    return (repo / rel_norm).resolve()


def run_aggregation_preflight(
    *,
    repo: Path,
    rollup_blob: dict[str, Any],
    fingerprint: dict[str, Any],
    sealed_index: dict[str, Any],
) -> list[PreflightResult]:
    results: list[PreflightResult] = []
    lanes = rollup_blob.get("lanes") or {}
    pointers = {str(p["lane"]): p for p in (sealed_index.get("pointers") or []) if isinstance(p, dict)}

    # Digest coherence (JD/briefing targeting plane — not proof)
    mixed_run = not bool(fingerprint.get("same_date_prefix_coherent"))
    results.append(
        PreflightResult(
            gate_id="x2_preflight_mixed_run_ids_recorded",
            pass_=True,
            decisive_reason="mixed run_id date prefixes" if mixed_run else None,
            observed={
                "same_date_prefix_coherent": fingerprint.get("same_date_prefix_coherent"),
                "lane_run_ids": fingerprint.get("lane_run_ids"),
                "mixed_run": mixed_run,
            },
        ),
    )

    jd_coh = fingerprint.get("jd_digest_coherent")
    jd_ok = jd_coh not in ("MISMATCH",)
    results.append(
        PreflightResult(
            gate_id="x2_preflight_jd_digest_coherence",
            pass_=jd_ok,
            decisive_reason=None if jd_ok else f"conflicting jd_text_hash across lanes: {jd_coh}",
            observed=jd_coh,
        ),
    )

    br_coh = fingerprint.get("briefing_digest_coherent")
    br_ok = br_coh not in ("MISMATCH",)
    results.append(
        PreflightResult(
            gate_id="x2_preflight_briefing_digest_coherence",
            pass_=br_ok,
            decisive_reason=None if br_ok else f"conflicting briefing_hash across lanes: {br_coh}",
            observed=br_coh,
        ),
    )

    missing_proof: list[str] = []
    pool_fail_lanes: list[str] = []
    x2_fail_lanes: list[str] = []
    review_block_lanes: list[str] = []
    blocked_lanes: list[str] = []

    for lane in GENERATED_LANE_IDS:
        row = lanes.get(lane)
        ptr = pointers.get(lane)
        if not isinstance(row, dict):
            missing_proof.append(f"{lane}:missing_rollup_lane")
            continue
        rd = row.get("latest_successful_real_artifact_path") or row.get("rollup_source_run_dir")
        if not isinstance(rd, str):
            missing_proof.append(f"{lane}:missing_run_dir")
            continue
        run_dir = _resolved_run_dir(repo, rd)
        for fname in REQUIRED_PROOF_FILES:
            if not (run_dir / fname).is_file():
                missing_proof.append(f"{lane}:{fname}")

        x2f = int(row.get("x2_failed") or 0)
        if x2f > 0:
            x2_fail_lanes.append(lane)

        code = str((ptr or {}).get("x3_code") or row.get("x3_code") or "")
        if _is_blocked_x3(code):
            blocked_lanes.append(lane)
        elif _is_review_x3(code):
            pq = str((ptr or {}).get("product_quality_status") or "")
            if pq == "FAIL":
                review_block_lanes.append(lane)

        pool_st = str((ptr or {}).get("pool_receipt_status") or "")
        if pool_st == "FAIL":
            pool_fail_lanes.append(lane)
        elif not pool_st and not (run_dir / "x2_source_fact_pool_receipt.json").is_file():
            pool_fail_lanes.append(f"{lane}:missing_pool_receipt")

    results.append(
        PreflightResult(
            gate_id="x2_preflight_required_proof_artifacts_present",
            pass_=not missing_proof,
            decisive_reason=None if not missing_proof else f"missing: {missing_proof[:8]}",
            observed=missing_proof,
        ),
    )
    results.append(
        PreflightResult(
            gate_id="x2_preflight_section_x2_all_pass",
            pass_=not x2_fail_lanes,
            decisive_reason=None if not x2_fail_lanes else f"x2_failed lanes: {x2_fail_lanes}",
            observed=x2_fail_lanes,
        ),
    )
    results.append(
        PreflightResult(
            gate_id="x2_preflight_pool_receipt_pass",
            pass_=not pool_fail_lanes,
            decisive_reason=None if not pool_fail_lanes else f"pool receipt fail/missing: {pool_fail_lanes}",
            observed=pool_fail_lanes,
        ),
    )
    results.append(
        PreflightResult(
            gate_id="x2_preflight_no_blocked_x3",
            pass_=not blocked_lanes,
            decisive_reason=None if not blocked_lanes else f"blocked x3 lanes: {blocked_lanes}",
            observed=blocked_lanes,
        ),
    )
    results.append(
        PreflightResult(
            gate_id="x2_preflight_no_review_without_product_pass",
            pass_=not review_block_lanes,
            decisive_reason=None if not review_block_lanes else f"REVIEW with non-PASS product quality: {review_block_lanes}",
            observed=review_block_lanes,
        ),
    )

    return results


def assert_preflight_pass(results: list[PreflightResult]) -> None:
    failed = [r for r in results if not r.pass_]
    if failed:
        raise AggregationPreflightError([r.to_dict() for r in failed])
