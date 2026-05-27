#!/usr/bin/env python3
"""Compare W3 Brown exec_summary run vs 230615 baseline (W3.1 acceptance matrix)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_230615"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _gate_pass_map(x2_path: Path) -> dict[str, bool]:
    raw = _load(x2_path)
    gates = raw.get("gates") or raw.get("gate_results") or []
    out: dict[str, bool] = {}
    if isinstance(gates, list):
        for g in gates:
            if isinstance(g, dict) and g.get("gate_id"):
                out[str(g["gate_id"])] = bool(g.get("pass"))
    elif isinstance(gates, dict):
        for gid, g in gates.items():
            if isinstance(g, dict):
                out[str(gid)] = bool(g.get("pass"))
            else:
                out[str(gid)] = bool(g)
    return out


def _cycles_summary(cycles_path: Path) -> dict[str, Any]:
    raw = _load(cycles_path)
    cycles = raw.get("cycles") or []
    last = cycles[-1] if cycles else {}
    stopped = raw.get("stopped_reason") or last.get("stopped_reason")
    regen_lane = raw.get("regen_lane_stats") or {}
    claim_gate_cycles = 0
    for c in cycles:
        if not isinstance(c, dict):
            continue
        gids = c.get("post_regen_x2_failed_gate_ids") or []
        if "x2_claim_field_maps_to_display_sentence" in gids:
            claim_gate_cycles += 1
    return {
        "max_cycles": raw.get("max_cycles"),
        "cycles_recorded": len(cycles),
        "stopped_reason": stopped,
        "stuck_loop_detected": regen_lane.get("stuck_loop_detected"),
        "stuck_signature": regen_lane.get("stuck_signature"),
        "claim_field_map_fail_cycles": claim_gate_cycles,
        "transport_attempts_total": raw.get("transport_attempts_total"),
    }


def compare_runs(new_dir: Path, baseline_dir: Path = BASELINE) -> dict[str, Any]:
    cli_new = _load(new_dir / "cli_section_execution_report.json")
    cli_base = _load(baseline_dir / "cli_section_execution_report.json")
    x2_new = _gate_pass_map(new_dir / "x2_gate_outputs.json")
    x2_base = _gate_pass_map(baseline_dir / "x2_gate_outputs.json")
    claim_new = x2_new.get("x2_claim_field_maps_to_display_sentence")
    claim_base = x2_base.get("x2_claim_field_maps_to_display_sentence")
    cycles_new = _cycles_summary(new_dir / "judge_remediation_cycles.json")
    cycles_base = _cycles_summary(baseline_dir / "judge_remediation_cycles.json")
    return {
        "new_run_dir": new_dir.as_posix(),
        "baseline_run_dir": baseline_dir.as_posix(),
        "cli": {
            "new": {
                "operator_status": cli_new.get("operator_status"),
                "product_status": cli_new.get("product_status"),
                "x2_product_quality_status": cli_new.get("x2_product_quality_status"),
                "draft_ready": cli_new.get("draft_ready"),
            },
            "baseline": {
                "operator_status": cli_base.get("operator_status"),
                "product_status": cli_base.get("product_status"),
                "x2_product_quality_status": cli_base.get("x2_product_quality_status"),
                "draft_ready": cli_base.get("draft_ready"),
            },
        },
        "x2_claim_field_maps_to_display_sentence": {
            "new": claim_new,
            "baseline": claim_base,
            "improved": claim_base is False and claim_new is True,
        },
        "regen_cycles": {"new": cycles_new, "baseline": cycles_base},
        "w3_acceptance_hints": {
            "draft_ready_or_allow": cli_new.get("draft_ready") is True
            or cli_new.get("product_status") == "X3_ALLOW",
            "claim_gate_improved_or_stuck_exit": (
                claim_new is True
                or cycles_new.get("stopped_reason") == "x2_stuck_same_failure"
                or (cycles_new.get("cycles_recorded", 99) < cycles_base.get("cycles_recorded", 0))
            ),
            "stuck_not_same_exhaust_as_baseline": cycles_new.get("stopped_reason")
            != cycles_base.get("stopped_reason")
            or cycles_new.get("cycles_recorded", 0) < cycles_base.get("cycles_recorded", 99),
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("new_run_dir", type=Path, help="W3 artifact directory")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    report = compare_runs(args.new_run_dir.resolve())
    hints = report["w3_acceptance_hints"]
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"compare: new={report['new_run_dir']}")
        print(f"  claim_gate new={report['x2_claim_field_maps_to_display_sentence']['new']} "
              f"baseline={report['x2_claim_field_maps_to_display_sentence']['baseline']}")
        print(f"  regen new cycles={report['regen_cycles']['new']}")
        print(f"  w3_hints={hints}")
    ok = all(hints.values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
