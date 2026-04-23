#!/usr/bin/env python3
"""Wiring-CI trend report (plan W5.2).

Reads `artifacts/windsurf/wiring_gate_violations.jsonl`, rolls up each
gate's violation count over the most-recent N runs, and writes a markdown
report to `docs/reports/wiring-ci/<UTC-date>.md`. Intended as a lightweight
daily / weekly pulse — not a gate.

Run:
    python tools/reports/wiring_ci_trend.py
    python tools/reports/wiring_ci_trend.py --runs 20 --output docs/reports/wiring-ci/custom.md

Exit codes:
    0 — report written (or no data)
    2 — runner error
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = REPO_ROOT / "artifacts" / "windsurf" / "wiring_gate_violations.jsonl"
OUT_DIR = REPO_ROOT / "docs" / "reports" / "wiring-ci"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"

GATE_ORDER = [
    "J1_canonical_pipeline_wiring",
    "A1_orphan_module_ratchet",
    "A3_dead_public_symbol_ratchet",
    "A6_import_cycle",
    "E1_trace_stub_module",
    "G2_seam_test_export_coherence",
    "L1_layer_gravity",
    "L2_lpg_drift_ratchet",
    "M1_module_loc_ratchet",
    "D1_layer_doc_binding",
    "S1_global_state_mutation_ratchet",
    "S2_uwg_bypass_ratchet",
    "S3_exception_swallow_ratchet",
    "S4_unused_imports_ratchet",
    "W5_waiver_expiry",
]

TIER_OF = {
    "J1_canonical_pipeline_wiring": "B",
    "A1_orphan_module_ratchet": "R",
    "A3_dead_public_symbol_ratchet": "R",
    "A6_import_cycle": "B",
    "E1_trace_stub_module": "R",
    "G2_seam_test_export_coherence": "B",
    "L1_layer_gravity": "R",
    "L2_lpg_drift_ratchet": "R",
    "M1_module_loc_ratchet": "R",
    "D1_layer_doc_binding": "W",
    "S1_global_state_mutation_ratchet": "R",
    "S2_uwg_bypass_ratchet": "R",
    "S3_exception_swallow_ratchet": "R",
    "S4_unused_imports_ratchet": "R",
    "W5_waiver_expiry": "B",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=10, help="Number of most-recent runs per gate to include")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Override default output path (default: docs/reports/wiring-ci/<UTC-date>.md)",
    )
    args = parser.parse_args(argv)

    if not LOG_FILE.exists():
        print(f"No sink at {LOG_FILE}; nothing to report.")
        return 0

    per_gate = _load_per_gate_runs(LOG_FILE, args.runs)
    baselines = _load_baselines()
    report = _render_report(per_gate, baselines, args.runs)

    out = args.output or OUT_DIR / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT).as_posix()}")
    return 0


def _load_per_gate_runs(path: Path, max_per_gate: int) -> dict[str, list[dict]]:
    per_gate: dict[str, list[dict]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        gid = row.get("gate_id")
        if not gid:
            continue
        per_gate[gid].append(row)
    # Trim to most-recent N per gate.
    trimmed: dict[str, list[dict]] = {}
    for gid, runs in per_gate.items():
        # Preserve original order (append-only log); take tail.
        trimmed[gid] = runs[-max_per_gate:]
    return trimmed


def _load_baselines() -> dict[str, int]:
    baselines: dict[str, int] = {}
    if not BASELINE_DIR.is_dir():
        return baselines
    for path in BASELINE_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        gid = data.get("gate_id")
        count = data.get("count")
        if gid and isinstance(count, int):
            baselines[gid] = count
    return baselines


def _render_report(per_gate: dict[str, list[dict]], baselines: dict[str, int], runs: int) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = [
        "# Wiring-CI Trend Report",
        "",
        f"**Generated:** {now}  ",
        f"**Runs per gate:** last {runs}  ",
        f"**Source log:** `{LOG_FILE.relative_to(REPO_ROOT).as_posix()}`",
        "",
        "## Current State",
        "",
        "| Gate | Tier | Last | Baseline | Δ vs baseline | Status |",
        "|---|:-:|:-:|:-:|:-:|:-:|",
    ]
    ordered: OrderedDict[str, list[dict]] = OrderedDict()
    for gid in GATE_ORDER:
        if gid in per_gate:
            ordered[gid] = per_gate[gid]
    for gid, runs_list in per_gate.items():
        ordered.setdefault(gid, runs_list)

    for gid, runs_list in ordered.items():
        if not runs_list:
            continue
        tier = TIER_OF.get(gid, "?")
        last = runs_list[-1]
        last_count = _active_count(last)
        baseline = baselines.get(gid)
        delta_cell: str
        if baseline is None:
            delta_cell = "—"
        else:
            diff = last_count - baseline
            if diff == 0:
                delta_cell = "0"
            elif diff > 0:
                delta_cell = f"+{diff}"
            else:
                delta_cell = str(diff)
        status = last.get("status", "?")
        lines.append(
            f"| `{gid}` | {tier} | {last_count} | "
            f"{baseline if baseline is not None else '—'} | {delta_cell} | {status} |"
        )

    lines.extend(["", "## Per-Gate History (active violation count)", ""])
    for gid, runs_list in ordered.items():
        if not runs_list:
            continue
        lines.append(f"### `{gid}` (tier {TIER_OF.get(gid, '?')})")
        lines.append("")
        lines.append("| # | Timestamp | Snapshot | Status | Active |")
        lines.append("|:-:|---|---|:-:|:-:|")
        for i, row in enumerate(runs_list, 1):
            lines.append(
                f"| {i} | `{row.get('timestamp', '?')}` | "
                f"`{row.get('snapshot', '?')}` | {row.get('status', '?')} | "
                f"{_active_count(row)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- **B (blocking)** gates MUST have `status=pass` for CI to go green.",
            "- **R (ratchet)** gates MUST have `Δ vs baseline <= 0` to pass.",
            "- **W (warn)** gates never block CI; trend is diagnostic.",
            "- A positive delta on a ratchet means a regression landed or snapshot moved; investigate before ignoring.",
            "",
        ]
    )
    return "\n".join(lines)


def _active_count(row: dict[str, Any]) -> int:
    violations = row.get("violations") or []
    return len(violations)


if __name__ == "__main__":
    sys.exit(main())
