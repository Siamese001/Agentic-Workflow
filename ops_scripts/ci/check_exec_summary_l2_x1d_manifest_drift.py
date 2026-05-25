#!/usr/bin/env python3
"""CI gate — executive_summary L2/X1D input parity manifest invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.prompt_assembly.e0_examples import _EXEC_SUMMARY_POSITIVE_COMPILE_IDS
from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    MANIFEST_SCHEMA_PATH,
    generation_law_digest_text,
)


def main() -> int:
    errors: list[str] = []

    if "exec_summary_gold_base_resume_001" in _EXEC_SUMMARY_POSITIVE_COMPILE_IDS:
        errors.append("gold_base must not be in _EXEC_SUMMARY_POSITIVE_COMPILE_IDS")
    if not _EXEC_SUMMARY_POSITIVE_COMPILE_IDS or _EXEC_SUMMARY_POSITIVE_COMPILE_IDS[0] != (
        "exec_summary_pos_svp_it_strategy_001"
    ):
        errors.append(
            f"first E0 compile id must be exec_summary_pos_svp_it_strategy_001, got {_EXEC_SUMMARY_POSITIVE_COMPILE_IDS[:1]}"
        )

    if not MANIFEST_SCHEMA_PATH.is_file():
        errors.append(f"missing schema {MANIFEST_SCHEMA_PATH}")
    else:
        schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
        if schema.get("properties", {}).get("schema", {}).get("const") != "generation_grade_contract_manifest_v1":
            errors.append("manifest schema version const mismatch")

    lane_src = (REPO_ROOT / "apps_rg/runtime/sections/executive_summary_lane.py").read_text(encoding="utf-8")
    if "defer_x1d_gates=True" not in lane_src:
        errors.append("lane must pass defer_x1d_gates=True to run_x2_gates")
    if "refresh_x1d_judges_after_full_x2" not in lane_src:
        errors.append("lane must call refresh_x1d_judges_after_full_x2 after structural X2")
    if "prior_judges=[]" not in lane_src:
        errors.append("post-X2 judge refresh must use prior_judges=[] (no pre-X2 MODEL_BACKED)")

    jp_src = (REPO_ROOT / "apps_rg/runtime/judges/executive_summary_judge_packet.py").read_text(
        encoding="utf-8"
    )
    if "GENERATION_LAW_DIGEST" not in jp_src:
        errors.append("judge packet render must include GENERATION_LAW_DIGEST")
    if "x2_executive_summary_synthesis_quality" not in jp_src:
        errors.append("build_deterministic_gate_summary must include synthesis_quality gate")
    if "generation_law_digest_text(" not in jp_src:
        errors.append("generation_law_digest_text must be referenced in judge_packet module")

    from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_no_credential_dump

    bad = (
        "Platform leader. "
        "Building on governed systems. "
        "Monolithic architecture. "
        "Advanced quantitative depth supported by AWS and Databricks certifications. "
        "Outcomes stay grounded. "
        "Capstone integrates delivery."
    )
    ok, reason = check_exec_summary_no_credential_dump(bad)
    if ok:
        errors.append("credential gate must fail named cert labels in closing band")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1
    print("PASS: exec_summary_l2_x1d_manifest_drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
