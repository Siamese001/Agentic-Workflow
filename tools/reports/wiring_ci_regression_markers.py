#!/usr/bin/env python3
"""Emit DEFERRED_SCOPE markers + writeback receipts for wiring-CI regressions.

Reads the most-recent run of each ratchet gate from
`artifacts/windsurf/wiring_gate_violations.jsonl`, compares against the
baseline, and emits:

1. One `DEFERRED_SCOPE:` marker per ratchet that is above baseline — lines
   Constitutional §24 recognizes, post-hook auto-posts to Notion
   Wave/Phase Convergence DB.
2. A `WIRING_REGRESSION_DIGEST` section with one row per regressed ratchet.

Not a gate — invoked in two contexts:
    a) Manually when a human reviews a trend report and wants the
       regressions captured as Notion rows.
    b) From CI logs (future) — parsing these markers is how CI feeds the
       DEFERRED_SCOPE auto-capture path.

Run:
    python tools/reports/wiring_ci_regression_markers.py
    python tools/reports/wiring_ci_regression_markers.py --output markers.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = REPO_ROOT / "artifacts" / "windsurf" / "wiring_gate_violations.jsonl"
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"

# H1 consolidation (2026-04-23): Retired 5 wiring gates as pure duplicates
# of canonical/validation-plane gates. Their regressions now route through
# existing v_p1_ratchet / v_p2_ratchet / v_structural_conformance paths.
# gate_id -> (plan-slug, wave, phase, layer, fan_in_hint, surface, coverage_hint, tokens, reason)
RATCHET_META = {
    "A3_dead_public_symbol_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W2",
        "W2.3",
        "L_APP",
        20,
        "None",
        60.0,
        8000,
        "A3 dead public symbol ratchet regression",
    ),
    "E1_trace_stub_module": (
        "adg-wiring-ci-hardening-7a5d84",
        "W2",
        "W2.4",
        "L0",
        50,
        "Observability",
        75.0,
        10000,
        "E1 trace-theater module ratchet regression",
    ),
    "L2_lpg_drift_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W3",
        "W3.2",
        "L_PG",
        25,
        "State",
        65.0,
        9000,
        "L2 L_PG internal drift ratchet regression",
    ),
    "M1_module_loc_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W3",
        "W3.3",
        "L_APP",
        15,
        "None",
        50.0,
        6000,
        "M1 module LOC ratchet regression",
    ),
    "S2_uwg_bypass_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W4",
        "W4.2",
        "L2",
        80,
        "Write",
        90.0,
        20000,
        "S2 UWG bypass ratchet regression",
    ),
    "S4_unused_imports_ratchet": (
        "adg-wiring-ci-hardening-7a5d84",
        "W4",
        "W4.4",
        "L_APP",
        15,
        "None",
        55.0,
        7000,
        "S4 unused imports ratchet regression",
    ),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write markers to this file in addition to stdout",
    )
    args = parser.parse_args(argv)

    if not LOG_FILE.exists():
        print("no sink log; nothing to emit", file=sys.stderr)
        return 0

    latest = _latest_per_gate(LOG_FILE)
    baselines = _load_baselines()

    lines: list[str] = []
    header = (
        f"# Wiring-CI Regression Markers\n"
        f"# Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        "# One DEFERRED_SCOPE line per ratchet above baseline. Post-hook\n"
        "# post_cascade_deferred_scope_capture.py will auto-score P1..P5 and\n"
        "# auto-post to the Wave/Phase Convergence database per Constitutional §24.\n"
    )
    lines.append(header)

    regressions: list[tuple[str, int, int]] = []
    for gate_id, run in latest.items():
        meta = RATCHET_META.get(gate_id)
        if not meta:
            continue
        current = len(run.get("violations", []))
        baseline = baselines.get(gate_id, 0)
        if current <= baseline:
            continue
        regressions.append((gate_id, current, baseline))
        plan, wave, phase, layer, fan_in, surface, cov, tokens, reason = meta
        lines.append(
            f"DEFERRED_SCOPE: plan={plan} wave={wave} phase={phase} "
            f"layer={layer} fan_in={fan_in} surface={surface} "
            f"coverage_gap_pct={cov} est_tokens={tokens} "
            f'reason="{reason} (+{current - baseline} above baseline={baseline})"'
        )

    if not regressions:
        lines.append("# no regressions detected — all ratchets at or below baseline.")
    else:
        lines.append("\n## WIRING_REGRESSION_DIGEST\n")
        lines.append("| Gate | Current | Baseline | Delta |")
        lines.append("|---|--:|--:|--:|")
        for gate_id, cur, base in regressions:
            lines.append(f"| `{gate_id}` | {cur} | {base} | +{cur - base} |")

    output = "\n".join(lines) + "\n"
    sys.stdout.write(output)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")

    return 0


def _latest_per_gate(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        gid = row.get("gate_id")
        if gid:
            latest[gid] = row
    return latest


def _load_baselines() -> dict[str, int]:
    out: dict[str, int] = {}
    if not BASELINE_DIR.is_dir():
        return out
    for path in BASELINE_DIR.glob("wiring_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        gid = data.get("gate_id")
        count = data.get("count")
        if gid and isinstance(count, int):
            out[gid] = count
    return out


if __name__ == "__main__":
    sys.exit(main())
