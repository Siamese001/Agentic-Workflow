#!/usr/bin/env python3
"""Unified ADG-CI dispatcher (H3).

Single entry point for the wiring-CI gate fleet. Replaces three separate
tools deleted in H3:

    tools/generate/wiring_ci_report.py          (markdown report emitter)
    tools/reports/wiring_ci_trend.py            (markdown trend report)
    tools/reports/wiring_ci_regression_markers.py (P1-P5 priority scorer)

Design (per plan adg-wiring-ci-hardening-7a5d84 H3 row in Notion Wave/Phase
Convergence DB 34b27693-f55c-8110-bdab-dd477efb17e4):

    - GATES sourced from `unified_registry.WIRING_GATES` (single SSOT)
    - Orchestrates via subprocess fan-out (TODO H4: in-process ADGGateBase)
    - Emits ONE JSON artifact: artifacts/adg/adg_gate_results_<ts>.json
    - Appends to the existing JSONL sink for trend queries
    - No markdown generation — use `tools/adg/query.py` for trend views
    - Emits DEFERRED_SCOPE: lines to stdout for CI regressions (consumed by
      the post_cascade_deferred_scope_capture hook per Constitutional §24)

Exit code:
    0  — all BLOCK gates pass AND all RATCHET gates at-or-below baseline
    1  — any BLOCK violation OR any RATCHET regression

Usage:
    python -m ops_scripts.ci.adg_gates.run                    # full fleet
    python -m ops_scripts.ci.adg_gates.run --markers          # + DEFERRED_SCOPE
    python -m ops_scripts.ci.adg_gates.run --json-only        # suppress human print
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.adg_gates.unified_registry import (  # noqa: E402
    WIRING_GATES,
    GateSpec,
    Enforcement,
)

BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
RESULTS_DIR = REPO_ROOT / "artifacts" / "adg"
SINK_DIR = REPO_ROOT / "artifacts" / "windsurf"
SINK_FILE = SINK_DIR / "adg_gate_dispatcher.jsonl"

# ``_MARKER_META`` shape:
#   (plan-slug, wave, phase, layer, fan_in, surface, coverage_gap_pct, est_tokens, reason)
# Minimal map kept for DEFERRED_SCOPE emission.  Gates not listed here do not
# emit markers — they still fail the build, but do not auto-post to Notion.
# H3: replaces the P1-P5 priority scorer in the retired
# wiring_ci_regression_markers.py; priority is now sourced from
# `unified_registry.GateSpec.band` directly.
_MARKER_META: dict[str, tuple[str, str, str, str, int, str, float, int, str]] = {
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
    "G_REACH_l0_reachability": (
        "adg-wiring-ci-hardening-7a5d84",
        "H2",
        "H2.1",
        "L0",
        100,
        "Execution",
        95.0,
        14000,
        "G-REACH new L0-unreachable production module",
    ),
    "G_ISLAND_connected_components": (
        "adg-wiring-ci-hardening-7a5d84",
        "H2",
        "H2.2",
        "L_APP",
        20,
        "State",
        70.0,
        8000,
        "G-ISLAND new disconnected component cluster",
    ),
    "G_WATCHLIST_DELTA_hotspot_regressions": (
        "adg-wiring-ci-hardening-7a5d84",
        "H2",
        "H2.3",
        "L_APP",
        30,
        "Execution",
        65.0,
        9000,
        "G-WATCHLIST-DELTA graph hotspot regression",
    ),
}


def _run_gate(spec: GateSpec) -> dict[str, Any]:
    """Subprocess one gate and parse its summary line."""
    script_path = REPO_ROOT / spec.handler
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=180,
            check=False,
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except (subprocess.TimeoutExpired, OSError) as exc:
        exit_code = -1
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}"

    header = next(
        (
            line
            for line in stdout.splitlines()
            if line.startswith(f"[{spec.gate_id}]") and "violations=" in line
        ),
        "",
    )
    # Count from header ``violations=N``.
    count = -1
    if "violations=" in header:
        try:
            count = int(header.split("violations=")[1].split()[0])
        except (ValueError, IndexError):
            count = -1
    status = "unknown"
    for token in ("status=pass", "status=fail", "status=warn", "status=bypass"):
        if token in header:
            status = token.split("=")[1]
            break

    return {
        "gate_id": spec.gate_id,
        "band": spec.band.value,
        "enforcement": spec.enforcement.value,
        "source": spec.source.value,
        "owner": spec.owner,
        "handler": spec.handler,
        "exit_code": exit_code,
        "violation_count": count,
        "status": status,
        "stderr_tail": stderr.strip().splitlines()[-5:] if stderr.strip() else [],
    }


def _load_baseline(gate_id: str) -> int | None:
    """Baseline count for a RATCHET gate; None if no baseline file exists."""
    # Map gate_id to baseline filename (same convention as WiringGate.baseline_filename).
    name_map = {
        "A3_dead_public_symbol_ratchet": "wiring_dead_symbol_ratchet.json",
        "E1_trace_stub_module": "wiring_trace_stub_ratchet.json",
        "L2_lpg_drift_ratchet": "wiring_lpg_drift_ratchet.json",
        "M1_module_loc_ratchet": "wiring_module_loc_ratchet.json",
        "S2_uwg_bypass_ratchet": "wiring_uwg_bypass_ratchet.json",
        "S4_unused_imports_ratchet": "wiring_unused_imports_ratchet.json",
        "G_REACH_l0_reachability": "wiring_graph_reach_ratchet.json",
        "G_ISLAND_connected_components": "wiring_graph_island_ratchet.json",
        "G_WATCHLIST_DELTA_hotspot_regressions": "wiring_graph_watchlist_delta_ratchet.json",
    }
    filename = name_map.get(gate_id)
    if not filename:
        return None
    path = BASELINE_DIR / filename
    if not path.exists():
        return None
    try:
        return int(json.loads(path.read_text(encoding="utf-8")).get("count", 0))
    except (json.JSONDecodeError, ValueError, OSError):
        return None


def _classify(row: dict[str, Any]) -> str:
    """Derive human-friendly status using (enforcement, baseline, count)."""
    enf = row["enforcement"]
    count = row["violation_count"]
    baseline = _load_baseline(row["gate_id"])
    row["baseline_count"] = baseline
    if enf == "block":
        if row["exit_code"] == 0 and count == 0:
            return "pass"
        return "blocked" if row["exit_code"] != 0 else "warn"
    if enf == "ratchet":
        if baseline is None:
            return "seed_missing"
        if count <= baseline:
            return "pass"
        return "regressed"
    if enf == "warn":
        return "pass"
    return "unknown"


def _emit_marker(spec_id: str, delta: int) -> str | None:
    """Emit a single DEFERRED_SCOPE line for a ratchet regression."""
    meta = _MARKER_META.get(spec_id)
    if meta is None:
        return None
    plan, wave, phase, layer, fan_in, surface, coverage, tokens, reason = meta
    return (
        f"DEFERRED_SCOPE: plan={plan} wave={wave} phase={phase} "
        f"layer={layer} fan_in={fan_in} surface={surface} "
        f"coverage_gap_pct={coverage} est_tokens={tokens} "
        f"reason={reason} delta={delta}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--markers", action="store_true", help="Emit DEFERRED_SCOPE: lines to stdout for ratchet regressions."
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Suppress human-readable fleet summary; print only the JSON path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory for the adg_gate_results_<ts>.json artifact.",
    )
    args = parser.parse_args(argv)

    rows: list[dict[str, Any]] = []
    overall_exit = 0
    for spec in tqdm(WIRING_GATES, desc="ADG gates", unit="gate"):
        row = _run_gate(spec)
        classification = _classify(row)
        row["classification"] = classification
        rows.append(row)

        # Exit-code policy: any block fail OR any ratchet regression -> 1.
        if spec.enforcement == Enforcement.BLOCK and row["exit_code"] != 0:
            overall_exit = 1
        elif spec.enforcement == Enforcement.RATCHET and classification == "regressed":
            overall_exit = 1

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    payload = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_gates": len(rows),
        "overall_exit_code": overall_exit,
        "summary": {
            "block_pass": sum(
                1 for r in rows if r["enforcement"] == "block" and r["classification"] == "pass"
            ),
            "block_fail": sum(
                1 for r in rows if r["enforcement"] == "block" and r["classification"] != "pass"
            ),
            "ratchet_pass": sum(
                1 for r in rows if r["enforcement"] == "ratchet" and r["classification"] == "pass"
            ),
            "ratchet_regressed": sum(1 for r in rows if r["classification"] == "regressed"),
            "ratchet_seed_missing": sum(1 for r in rows if r["classification"] == "seed_missing"),
            "warn": sum(1 for r in rows if r["enforcement"] == "warn"),
        },
        "gates": rows,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"adg_gate_results_{ts}.json"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    # Append trend row to JSONL sink.
    SINK_DIR.mkdir(parents=True, exist_ok=True)
    with SINK_FILE.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "timestamp": payload["timestamp"],
                    "overall_exit_code": overall_exit,
                    "summary": payload["summary"],
                }
            )
            + "\n"
        )

    if not args.json_only:
        print(f"[adg_gates.run] {len(rows)} gates | overall_exit={overall_exit}")
        print(f"  Results JSON: {json_path}")
        for r in rows:
            base = r.get("baseline_count")
            base_str = f"baseline={base}" if base is not None else "baseline=—"
            print(
                f"  [{r['band']}] [{r['enforcement']:7s}] "
                f"{r['gate_id']:42s} "
                f"status={r['classification']:14s} "
                f"count={r['violation_count']:>5} "
                f"{base_str}"
            )
    else:
        print(str(json_path))

    if args.markers:
        for r in rows:
            if r["classification"] == "regressed":
                base = r.get("baseline_count") or 0
                marker = _emit_marker(r["gate_id"], r["violation_count"] - base)
                if marker:
                    print(marker)

    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main())
