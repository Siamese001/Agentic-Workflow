"""W5 — verify Anthropic-aligned surgical judge regen on a REAL_LLM artifact dir."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _resolve(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def verify(run_dir: Path) -> dict:
    report: dict = {
        "schema": "executive_summary_anthropic_surgical_regen_verify_v1",
        "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/")
        if run_dir.is_relative_to(ROOT)
        else str(run_dir).replace("\\", "/"),
        "checks": {},
        "passed": True,
    }

    cycles = _load_json(run_dir / "judge_remediation_cycles.json")
    if cycles is None:
        report["passed"] = False
        report["error"] = "missing or invalid judge_remediation_cycles.json"
        return report

    report["regen_outcome"] = cycles.get("regen_outcome")
    report["final_publish_baseline"] = cycles.get("final_publish_baseline")
    cycle_list = [c for c in (cycles.get("cycles") or []) if isinstance(c, dict)]
    report["checks"]["cycle_count"] = len(cycle_list)

    feedback_dropped = False
    for cycle in cycle_list:
        dropped = int(cycle.get("judge_feedback_lines_dropped") or 0)
        if dropped > 0:
            feedback_dropped = True
        g5 = cycle.get("g5_delta_scope")
        if isinstance(g5, dict):
            schema = str(g5.get("schema") or "")
            report["checks"].setdefault("g5_schemas", []).append(schema)
            if schema == "executive_summary_g5_delta_scope_v2":
                report["checks"]["g5v2_used"] = True
                if g5.get("allowlist_passed", g5.get("passed")):
                    report["checks"].setdefault("g5v2_passed_cycles", []).append(
                        cycle.get("cycle"),
                    )
                else:
                    report["checks"].setdefault("g5v2_failed_cycles", []).append(
                        cycle.get("cycle"),
                    )
            if int(g5.get("judge_feedback_lines_dropped") or 0) > 0:
                feedback_dropped = True

    report["checks"]["judge_feedback_never_truncated"] = not feedback_dropped
    if feedback_dropped:
        report["passed"] = False

    g5_files = sorted(run_dir.glob("g5_delta_scope_cycle_*.json"))
    report["checks"]["g5_artifact_count"] = len(g5_files)
    for g5_path in g5_files:
        g5_doc = _load_json(g5_path)
        if g5_doc is None:
            continue
        if g5_doc.get("schema") != "executive_summary_g5_delta_scope_v2":
            report["checks"]["all_g5_v2"] = False
            report["passed"] = False
        elif "allowlist" not in g5_doc:
            report["checks"]["all_g5_have_allowlist"] = False
            report["passed"] = False

    regen_reqs = sorted(
        list(run_dir.glob("provider_request_judge_regen_cycle*.json"))
        + list(run_dir.glob("provider_request_regen.json")),
    )
    edit_budget_ok = True
    regen_delta_seen = False
    for req_path in regen_reqs:
        payload = _load_json(req_path)
        if payload is None:
            continue
        messages = payload.get("messages") or []
        user_turns = [
            str(m.get("content") or "")
            for m in messages
            if isinstance(m, dict) and m.get("role") == "user"
        ]
        if len(user_turns) >= 2 and any("REGEN_DELTA" in t for t in user_turns):
            regen_delta_seen = True
        last_user = user_turns[-1] if user_turns else ""
        if "REGEN_DELTA" in last_user:
            if "freeze all other sentences verbatim" not in last_user:
                edit_budget_ok = False
            if "indexes" not in last_user and "no resume_display_text sentence edits" not in last_user:
                edit_budget_ok = False

    report["checks"]["regen_delta_user_turn_seen"] = regen_delta_seen
    report["checks"]["allowlist_edit_budget_in_delta"] = edit_budget_ok
    if regen_reqs and not edit_budget_ok:
        report["passed"] = False

    plan = _load_json(run_dir / "executive_summary_qwen_call_plan.json")
    if plan and isinstance(plan.get("calls"), list):
        regen_rows = [
            r
            for r in plan["calls"]
            if isinstance(r, dict) and str(r.get("phase") or "") == "judge_regen"
        ]
        indices = [int(r.get("semantic_regen_attempt_index") or 0) for r in regen_rows]
        report["checks"]["semantic_regen_attempt_indices"] = indices
        report["checks"]["semantic_index_monotonic"] = (
            len(indices) <= 1 or indices == sorted(indices)
        )

    cli = _load_json(run_dir / "cli_section_execution_report.json")
    if cli:
        report["operator_status"] = cli.get("OPERATOR_STATUS") or cli.get("operator_status")
        report["product_status"] = cli.get("PRODUCT_STATUS") or cli.get("product_status")

    x3 = _load_json(run_dir / "x3_disposition.json")
    if x3:
        report["x3_code"] = x3.get("x3_code") or x3.get("disposition")

    report["checks"]["w5_infrastructure_ok"] = bool(
        report["checks"].get("judge_feedback_never_truncated")
        and report["checks"].get("g5v2_used")
        and report["checks"].get("allowlist_edit_budget_in_delta")
    )
    if not report["checks"].get("w5_infrastructure_ok"):
        report["passed"] = False

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", help="exec_summary_* run directory")
    parser.add_argument("--write-receipt", default="", help="Optional JSON receipt path")
    args = parser.parse_args()
    run_dir = _resolve(args.artifact_dir)
    if not run_dir.is_dir():
        print(json.dumps({"passed": False, "error": f"not a directory: {run_dir}"}, indent=2))
        return 2
    report = verify(run_dir)
    if args.write_receipt:
        out = _resolve(args.write_receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
