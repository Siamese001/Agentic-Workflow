"""Print apps_rg/apps_eval microstep and diagnostic granularity inventory."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from apps_eval.coverage import build_apps_rg_microstep_evaluation, load_apps_rg_contracts
from apps_eval.contracts import AppOutputSnapshot
from apps_eval.diagnostics import build_apps_rg_diagnostics


def _counter(rows: list[Any], attr: str) -> dict[str, int]:
    counts = Counter(str(getattr(row, attr) or "") for row in rows)
    counts.pop("", None)
    return {key: counts[key] for key in sorted(counts)}


def build_inventory() -> dict[str, Any]:
    contracts = load_apps_rg_contracts()
    snapshot = AppOutputSnapshot(
        app_id="apps_rg",
        scenario_id="granularity_inventory",
        x3_disposition="X3D_ALLOW_FINISH",
        output={"sections": {}},
    )
    evaluation = build_apps_rg_microstep_evaluation(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="granularity_inventory",
        snapshot=snapshot,
        run_id="granularity-inventory",
        created_at="1970-01-01T00:00:00Z",
        planned_eval_artifacts={
            "scorecard_rows": "scorecard_rows.jsonl",
            "component_scorecards": "apps_rg_component_scorecard.json",
            "coverage_matrix": "coverage_matrix.csv",
            "regression_summary": "regression.json",
        },
    )
    rows = list(evaluation["rows"])
    record_rows = [row for row in rows if row.required or row.artifact_ref]
    diagnostics = build_apps_rg_diagnostics(
        suite_id="apps_rg.dev.resume_generation",
        scenario_id="granularity_inventory",
        snapshot=snapshot,
        run_id="granularity-inventory",
        scorecard_rows=record_rows,
    )
    diagnostic_rows = list(diagnostics["rows"])
    optional_omitted = [row for row in rows if not row.required and not row.artifact_ref]
    return {
        "schema_version": "apps_eval.apps_rg_granularity_inventory.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "app_id": "apps_rg",
        "suite_id": "apps_rg.dev.resume_generation",
        "lane_count": len(contracts["lane_contract"].get("generated_lanes", [])),
        "raw_microstep_rows_per_scenario": len(rows),
        "record_level_rows_per_scenario": len(record_rows),
        "optional_rows_omitted_from_record_scorecards": len(optional_omitted),
        "rows_by_stage": _counter(rows, "stage_id"),
        "rows_by_lane": _counter(rows, "lane_id"),
        "rows_by_gate_id": _counter(rows, "gate_id"),
        "diagnostic_count": len(diagnostic_rows),
        "diagnostics_by_family": _counter(diagnostic_rows, "diagnostic_family"),
        "diagnostics_by_stage": _counter(diagnostic_rows, "stage_id"),
        "diagnostics_by_lane": _counter(diagnostic_rows, "lane_id"),
        "diagnostics_by_verdict": _counter(diagnostic_rows, "diagnostic_verdict"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default="artifacts/apps_eval/granularity_inventory",
        help="Directory for optional inventory JSON output.",
    )
    parser.add_argument("--write-artifact", action="store_true")
    args = parser.parse_args(argv)

    inventory = build_inventory()
    print(json.dumps(inventory, indent=2, sort_keys=True))
    if args.write_artifact:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "apps_rg_apps_eval_granularity_inventory.json"
        path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
