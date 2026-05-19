"""W11 per-lane blocker RCA JSON emitter."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

REPO = find_repo_root()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_lane_rca(*, lane: str, run_dir: Path) -> dict[str, Any]:
    x3 = _load(run_dir / "x3_disposition.json")
    x2 = _load(run_dir / "x2_gate_outputs.json") if (run_dir / "x2_gate_outputs.json").is_file() else {}
    pool = _load(run_dir / "x2_source_fact_pool_receipt.json") if (run_dir / "x2_source_fact_pool_receipt.json").is_file() else {}
    judges = _load(run_dir / "x1d_llm_judge_outputs.json") if (run_dir / "x1d_llm_judge_outputs.json").is_file() else {}
    jp = _load(run_dir / f"{lane}_judge_packet.json") if (run_dir / f"{lane}_judge_packet.json").is_file() else {}

    blockers: list[str] = []
    if x3.get("runtime_generation_status") == "OFFLINE_CONTRACT_STUB":
        blockers.append("OFFLINE_CONTRACT_STUB")
    if "REVIEW" in str(x3.get("x3_code") or ""):
        blockers.append("X3_review_disposition")
    if x3.get("soft_failed_judges"):
        blockers.append("judge_soft_fail")
    if int(x2.get("x2_failed") or 0) > 0:
        blockers.append("x2_failure")
    if jp.get("allowed_fact_packet") is None:
        blockers.append("proof_pool_mismatch")
    if pool.get("proof_pool_ref") and "base_resume" in str(pool.get("proof_pool_ref")):
        blockers.append("proof_pool_policy_mismatch")

    judge_rows = []
    for j in judges.get("judges") or []:
        if not isinstance(j, dict):
            continue
        judge_rows.append(
            {
                "provider_key": j.get("provider_key"),
                "provider_status": j.get("provider_status"),
                "score": j.get("score"),
                "pass": j.get("pass"),
                "fail_reasons": j.get("fail_reasons") or [],
                "unsupported_claims": j.get("unsupported_claims") or [],
                "quality_flags": j.get("quality_flags") or [],
            },
        )

    return {
        "schema": f"apps_rg.{lane}_blocker_rca.v1",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "lane": lane,
        "run_id": run_dir.name,
        "artifact_dir": run_dir.relative_to(REPO).as_posix(),
        "x3_code": x3.get("x3_code"),
        "runtime_generation_status": x3.get("runtime_generation_status"),
        "product_quality_status": x3.get("product_quality_status"),
        "x2_failed": int(x2.get("x2_failed") or 0),
        "blocker_classes": blockers,
        "proof_pool_ref": pool.get("proof_pool_ref"),
        "judge_packet_allowed_fact_packet_null": jp.get("allowed_fact_packet") is None,
        "soft_failed_judges": x3.get("soft_failed_judges") or [],
        "x2_failed_gate_ids": x3.get("x2_failed_gates") or [],
        "judge_summary": judge_rows,
        "artifact_refs": {
            "x3_disposition.json": (run_dir / "x3_disposition.json").relative_to(REPO).as_posix(),
            "x2_gate_outputs.json": (run_dir / "x2_gate_outputs.json").relative_to(REPO).as_posix(),
            "x1d_llm_judge_outputs.json": (run_dir / "x1d_llm_judge_outputs.json").relative_to(REPO).as_posix(),
            "judge_packet.json": (run_dir / f"{lane}_judge_packet.json").relative_to(REPO).as_posix()
            if (run_dir / f"{lane}_judge_packet.json").is_file()
            else None,
        },
        "minimal_fix": (
            "Pass allowed_fact_packet (IBM facts slice) into judge packet; regenerate REAL_LLM"
            if lane == "ibm_bullets"
            else "Pin existing X3_ALLOW run or strengthen claim_ledger fact_ids for anthropic judge"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run_dir = REPO / "artifacts/apps_rg/runtime_proofs" / args.lane / "real" / args.run_id
    blob = build_lane_rca(lane=args.lane, run_dir=run_dir)
    out = REPO / "artifacts/apps_rg/runtime_proofs/final_resume_assembly" / f"{args.lane}_blocker_rca.json"
    if args.write:
        out.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO)}")
    else:
        print(json.dumps(blob, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
