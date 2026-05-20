"""W8 blocked-lane audit — classify non-product-ALLOW lanes and emit fix plan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.aggregation.preflight import REQUIRED_PROOF_FILES
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

AUDIT_LANES = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "ibm_narrative",
    "ibm_bullets",
)

BLOCKER_TYPES = (
    "OFFLINE_CONTRACT_STUB",
    "mocked_judge",
    "judge_soft_fail",
    "pool_receipt_mismatch",
    "proof_pool_policy_mismatch",
    "missing_real_llm_artifact",
    "x2_failure",
    "x3_review_disposition",
    "x3_mock_plumbing",
    "missing_proof_artifact",
    "product_allow_eligible",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _classify_blockers(run_dir: Path | None) -> dict[str, Any]:
    if run_dir is None or not run_dir.is_dir():
        return {
            "rollup_run_dir": None,
            "blockers": ["missing_real_llm_artifact"],
            "minimal_fix": "regenerate with --provider qwen_vllm; no --mock-judges",
        }

    missing = [f for f in REQUIRED_PROOF_FILES if not (run_dir / f).is_file()]
    if missing:
        return {
            "rollup_run_dir": str(run_dir),
            "blockers": ["missing_proof_artifact"],
            "missing_files": missing,
            "minimal_fix": "regenerate lane until REQUIRED_PROOF_FILES present",
        }

    x3 = _load(run_dir / "x3_disposition.json")
    x2 = _load(run_dir / "x2_gate_outputs.json")
    pool = _load(run_dir / "x2_source_fact_pool_receipt.json")
    l2 = _load(run_dir / "l2_output.json")

    blockers: list[str] = []
    x3_code = str(x3.get("x3_code") or "")
    rgs = str(x3.get("runtime_generation_status") or "")
    auth = str(x3.get("authorization_scope") or "")
    pq = str(l2.get("product_quality_status") or "")
    x2f = int(x2.get("x2_failed") or 0)
    pool_st = str(pool.get("x2_source_fact_pool_status") or "")

    if x2f > 0:
        blockers.append("x2_failure")
    if pool_st != "PASS":
        blockers.append("pool_receipt_mismatch")
    if rgs == "OFFLINE_CONTRACT_STUB":
        blockers.append("OFFLINE_CONTRACT_STUB")
    if rgs != "REAL_LLM" and rgs:
        blockers.append("missing_real_llm_artifact")
    if x3.get("mocked_judges"):
        blockers.append("mocked_judge")
    if x3.get("soft_failed_judges"):
        blockers.append("judge_soft_fail")
    if "MOCK" in x3_code.upper() or "PLUMBING" in x3_code.upper() or auth == "PLUMBING_ONLY":
        blockers.append("x3_mock_plumbing")
    elif "REVIEW" in x3_code.upper():
        blockers.append("x3_review_disposition")

    product_allow = (
        x3_code == "X3_ALLOW"
        and rgs == "REAL_LLM"
        and x2f == 0
        and pool_st == "PASS"
        and pq != "FAIL"
        and "x3_mock_plumbing" not in blockers
        and "x3_review_disposition" not in blockers
        and "OFFLINE_CONTRACT_STUB" not in blockers
    )
    if product_allow:
        blockers = ["product_allow_eligible"]

    fix = "pin existing product-ALLOW run in coherent rollup"
    if "OFFLINE_CONTRACT_STUB" in blockers or "x3_mock_plumbing" in blockers:
        fix = "regenerate: python -m apps_rg --section <lane> --provider qwen_vllm --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude --allow-non-allow-exit-zero"
    elif "x3_review_disposition" in blockers or "judge_soft_fail" in blockers:
        fix = "regenerate with live judges; resolve soft-fail root cause (no mock judges)"
    elif "x2_failure" in blockers or "pool_receipt_mismatch" in blockers:
        fix = "fix X2/pool gate failures then regenerate"

    return {
        "rollup_run_dir": str(run_dir),
        "x3_code": x3_code,
        "runtime_generation_status": rgs,
        "authorization_scope": auth,
        "product_quality_status": pq,
        "x2_failed": x2f,
        "pool_receipt_status": pool_st,
        "proof_pool_ref": pool.get("proof_pool_ref"),
        "blockers": blockers,
        "product_allow_eligible": product_allow,
        "minimal_fix": fix,
    }


def _best_product_run(repo: Path, lane: str) -> Path | None:
    root = repo / "artifacts/apps_rg/runtime_proofs" / lane / "real"
    if not root.is_dir():
        return None
    for d in sorted(root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        row = _classify_blockers(d)
        if row.get("product_allow_eligible"):
            return d
    return None


def audit_blocked_lanes(*, repo: Path, rollup_path: Path) -> dict[str, Any]:
    rollup = _load(rollup_path) if rollup_path.is_file() else {"lanes": {}}
    lanes = rollup.get("lanes") if isinstance(rollup.get("lanes"), dict) else {}
    matrix: list[dict[str, Any]] = []

    for lane in AUDIT_LANES:
        row = lanes.get(lane) if isinstance(lanes, dict) else None
        rd = None
        if isinstance(row, dict):
            rel = row.get("latest_successful_real_artifact_path") or row.get("rollup_source_run_dir")
            if isinstance(rel, str):
                rd = (repo / rel.replace("\\", "/")).resolve()
        audit_row = _classify_blockers(rd)
        audit_row["lane"] = lane
        best = _best_product_run(repo, lane)
        audit_row["best_product_allow_run_in_repo"] = best.name if best else None
        matrix.append(audit_row)

    return {
        "schema": "apps_rg.blocked_lane_matrix.v1",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rollup_id": rollup.get("rollup_id"),
        "lanes": matrix,
        "regeneration_required": [
            m["lane"]
            for m in matrix
            if not m.get("product_allow_eligible") and not m.get("best_product_allow_run_in_repo")
        ],
        "rollup_pin_only": [
            m["lane"]
            for m in matrix
            if not m.get("product_allow_eligible") and m.get("best_product_allow_run_in_repo")
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="W8 blocked-lane audit")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    repo = find_repo_root()
    rollup_path = repo / "artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json"
    out_path = (
        Path(args.output)
        if args.output
        else repo / "artifacts/apps_rg/runtime_proofs/final_resume_assembly/blocked_lane_matrix.json"
    )
    blob = audit_blocked_lanes(repo=repo, rollup_path=rollup_path)
    if args.write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out_path.relative_to(repo)}")
    else:
        print(json.dumps(blob, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
