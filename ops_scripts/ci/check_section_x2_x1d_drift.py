#!/usr/bin/env python3
"""CI gate — all GENERATED_LANES X2 runtime vs X1D judge/product-shape contract alignment.

Per-lane: SSOT gates, alignment-matrix samples, rubric bounds, lane wiring.
Executive-summary: synthesis shape, judge packet snapshot, repair-loop order.

Bypass: ``SECTION_X2_X1D_DRIFT_BYPASS=1`` (legacy: ``EXEC_SUMMARY_X2_X1D_DRIFT_BYPASS=1``)
Advisory: ``SECTION_X2_X1D_DRIFT_ADVISORY=1`` (legacy: ``EXEC_SUMMARY_X2_X1D_DRIFT_ADVISORY=1``)

Usage:
    python ops_scripts/ci/check_section_x2_x1d_drift.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_x2_x1d_contract import (  # noqa: E402
    all_lane_x2_x1d_specs,
    audit_all_generated_lanes_x2_x1d_drift,
    extract_runtime_x2_gate_ids,
    lane_x2_x1d_spec,
)

ARTIFACT = REPO_ROOT / "artifacts" / "ci" / "section_x2_x1d_drift.json"
LEGACY_ARTIFACT = REPO_ROOT / "artifacts" / "ci" / "executive_summary_x2_x1d_drift.json"


def _bypassed() -> bool:
    return os.environ.get("SECTION_X2_X1D_DRIFT_BYPASS") == "1" or os.environ.get(
        "EXEC_SUMMARY_X2_X1D_DRIFT_BYPASS"
    ) == "1"


def _advisory() -> bool:
    return os.environ.get("SECTION_X2_X1D_DRIFT_ADVISORY") == "1" or os.environ.get(
        "EXEC_SUMMARY_X2_X1D_DRIFT_ADVISORY"
    ) == "1"


def _panel_harness_boundary_violations() -> list[dict[str, str]]:
    import subprocess

    script = REPO_ROOT / "ops_scripts" / "ci" / "check_judge_panel_harness_boundary.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return []
    detail = (proc.stderr or proc.stdout or "check_judge_panel_harness_boundary failed").strip()[:500]
    return [
        {
            "section_id": "agentic_core",
            "kind": "judge_panel_harness_boundary",
            "detail": detail,
            "path": str(script.relative_to(REPO_ROOT)),
        }
    ]


def main() -> int:
    if _bypassed():
        print("BYPASS — SECTION_X2_X1D_DRIFT_BYPASS=1")
        return 0

    violations = audit_all_generated_lanes_x2_x1d_drift()
    panel_v = _panel_harness_boundary_violations()
    if panel_v:
        from apps_rg.runtime.sections.section_x2_x1d_contract import X2X1dDriftViolation

        for pv in panel_v:
            violations.append(
                X2X1dDriftViolation(
                    pv["section_id"],
                    pv["kind"],
                    pv["detail"],
                    pv["path"],
                )
            )
    by_lane: dict[str, list[dict[str, str]]] = defaultdict(list)
    for v in violations:
        by_lane[v.section_id].append({"kind": v.kind, "detail": v.detail, "path": v.path})

    runtime_counts = {}
    for spec in all_lane_x2_x1d_specs():
        runtime_counts[spec.section_id] = len(
            extract_runtime_x2_gate_ids(
                x2_module_ref=spec.x2_module_ref,
                x2_run_function=spec.x2_run_function,
            )
        )

    payload = {
        "status": "PASS" if not violations else "FAIL",
        "lanes": list(GENERATED_LANES),
        "runtime_x2_gate_counts": runtime_counts,
        "violation_count": len(violations),
        "violations_by_lane": dict(by_lane),
        "violations": [
            {
                "section_id": v.section_id,
                "kind": v.kind,
                "detail": v.detail,
                "path": v.path,
            }
            for v in violations
        ],
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    LEGACY_ARTIFACT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if violations:
        print(f"FAIL — section X2/X1D drift ({len(violations)} violation(s) across {len(by_lane)} lane(s))")
        for lane in GENERATED_LANES:
            lane_v = by_lane.get(lane) or []
            if not lane_v:
                continue
            print(f"  [{lane}]")
            for item in lane_v:
                print(f"    [{item['kind']}] {item['detail']}")
        print(f"artifact: {ARTIFACT.relative_to(REPO_ROOT).as_posix()}")
        if _advisory():
            print("ADVISORY — SECTION_X2_X1D_DRIFT_ADVISORY=1 (exit 0)")
            return 0
        return 1

    counts = ", ".join(f"{k}={runtime_counts[k]}" for k in GENERATED_LANES)
    print(f"OK — all generated lanes X2/X1D aligned ({counts})")
    print(f"artifact: {ARTIFACT.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
