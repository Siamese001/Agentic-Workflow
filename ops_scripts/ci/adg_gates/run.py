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
    - Emits DEFERRED_SCOPE: lines to stdout for CI regressions (advisory stdout
      only — the post_agent_deferred_scope_capture consumer hook was retired in
      enforcement-surface-consolidation-d8b3f6 W7; native spawn_task supersedes
      the marker->hook->Notion pipeline per Constitutional §24 / ADR-096)

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
import importlib
import importlib.util
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.adg_gates.unified_registry import (  # noqa: E402
    CANONICAL_GATES,
    WIRING_GATES,
    Enforcement,
    GateSpec,
)

BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
RESULTS_DIR = REPO_ROOT / "artifacts" / "adg"
SINK_DIR = REPO_ROOT / "artifacts" / "governance"
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


# ---------------------------------------------------------------------------
# H4: in-process gate loader + dispatcher
# ---------------------------------------------------------------------------
_MODULE_CACHE: dict[str, Any] = {}


def _load_gate_class(spec: GateSpec) -> type | None:
    """Load the WiringGate subclass from ``spec.handler`` by spec.gate_class.

    Caches imported modules so consecutive gates from the same file share one
    module object. Returns ``None`` if the class or script is unavailable; the
    caller falls back to subprocess execution in that case.
    """
    if not spec.gate_class:
        return None
    script_path = REPO_ROOT / spec.handler
    if not script_path.exists():
        return None
    mod = _MODULE_CACHE.get(spec.handler)
    if mod is None:
        mod_name = f"_adg_gate_{script_path.stem}"
        module_spec = importlib.util.spec_from_file_location(mod_name, script_path)
        if module_spec is None or module_spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(module_spec)
        sys.modules[mod_name] = mod
        try:
            module_spec.loader.exec_module(mod)
        except (ImportError, SyntaxError, AttributeError):
            return None
        _MODULE_CACHE[spec.handler] = mod
    return getattr(mod, spec.gate_class, None)


def _run_gate_in_process(spec: GateSpec, snapshot: Path) -> dict[str, Any]:
    """Execute a gate in-process via WiringGate.execute(); return the row shape."""
    cls = _load_gate_class(spec)
    if cls is None:
        return _run_gate_subprocess(spec)  # defensive fallback

    stderr_tail: list[str] = []
    try:
        gate = cls(snapshot=snapshot)
        result = gate.execute()
        count = len(result.violations)
        status = result.status
        # Exit-code parity with ``cli_exit()``: fail -> 1; pass/warn/bypass -> 0.
        exit_code = 1 if status == "fail" else 0
    except (
        Exception
    ) as exc:  # guardian: allow-in-process-dispatcher -- isolate gate failures, don't crash fleet
        count = -1
        status = "error"
        exit_code = -1
        stderr_tail = traceback.format_exception(type(exc), exc, exc.__traceback__)[-5:]

    return {
        "gate_id": spec.gate_id,
        "band": spec.band.value,
        "enforcement": spec.enforcement.value,
        "source": spec.source.value,
        "owner": spec.owner,
        "handler": spec.handler,
        "gate_class": spec.gate_class,
        "dispatch": "in-process",
        "exit_code": exit_code,
        "violation_count": count,
        "status": status,
        "stderr_tail": [line.rstrip() for line in stderr_tail] if stderr_tail else [],
    }


def _run_gate_subprocess(spec: GateSpec) -> dict[str, Any]:
    """Legacy fallback: subprocess one gate and parse its summary line."""
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
        "gate_class": None,
        "dispatch": "subprocess",
        "exit_code": exit_code,
        "violation_count": count,
        "status": status,
        "stderr_tail": stderr.strip().splitlines()[-5:] if stderr.strip() else [],
    }


def _load_canonical_gate_class(spec: GateSpec) -> type | None:
    """Import a CANONICAL (ADGGateBase) gate class by dotted module path.

    For ``owner="adg_gates"`` rows, ``spec.handler`` is a dotted module path
    (e.g. ``ops_scripts.ci.adg_gates.gate_p0_critical_path``) and
    ``spec.gate_class`` is the ADGGateBase subclass.
    """
    if not spec.gate_class:
        return None
    try:
        mod = importlib.import_module(spec.handler)
    except (ImportError, SyntaxError, AttributeError):
        return None
    return getattr(mod, spec.gate_class, None)


def _run_canonical_gate_in_process(spec: GateSpec, snapshot: Path) -> dict[str, Any]:
    """Execute an ADGGateBase gate in-process; map status to the dispatcher row shape.

    ADGGateBase.status is ``"blocked" | "passed" | "warn"``; map:
        blocked -> exit_code=1, status="fail"
        passed  -> exit_code=0, status="pass"
        warn    -> exit_code=0, status="warn"
    """
    cls = _load_canonical_gate_class(spec)
    if cls is None:
        return _canonical_error_row(spec, "class_load_failed", [])

    stderr_tail: list[str] = []
    try:
        # ``emit_artifacts=False`` avoids CI_ARTIFACTS_DIR writes during a
        # fleet run — the dispatcher captures the gate JSON itself.
        gate = cls(sqlite_path=snapshot)
        result = gate.run(emit_artifacts=False)
        count = len(result.violations)
        raw_status = result.status
        if raw_status == "blocked":
            status, exit_code = "fail", 1
        elif raw_status == "warn":
            status, exit_code = "warn", 0
        else:
            status, exit_code = "pass", 0
    except Exception as exc:  # guardian: allow-in-process-dispatcher -- isolate canonical gate failures
        count = -1
        status = "error"
        exit_code = -1
        stderr_tail = traceback.format_exception(type(exc), exc, exc.__traceback__)[-5:]

    return {
        "gate_id": spec.gate_id,
        "band": spec.band.value,
        "enforcement": spec.enforcement.value,
        "source": spec.source.value,
        "owner": spec.owner,
        "handler": spec.handler,
        "gate_class": spec.gate_class,
        "dispatch": "in-process",
        "exit_code": exit_code,
        "violation_count": count,
        "status": status,
        "stderr_tail": [line.rstrip() for line in stderr_tail] if stderr_tail else [],
    }


def _canonical_error_row(spec: GateSpec, reason: str, stderr_tail: list[str]) -> dict[str, Any]:
    """Return a canonical-gate row representing a dispatcher-level failure."""
    return {
        "gate_id": spec.gate_id,
        "band": spec.band.value,
        "enforcement": spec.enforcement.value,
        "source": spec.source.value,
        "owner": spec.owner,
        "handler": spec.handler,
        "gate_class": spec.gate_class,
        "dispatch": "in-process",
        "exit_code": -1,
        "violation_count": -1,
        "status": "error",
        "error_reason": reason,
        "stderr_tail": stderr_tail,
    }


def _run_gate(spec: GateSpec, snapshot: Path | None = None) -> dict[str, Any]:
    """Dispatch one gate in-process if possible, else via subprocess fallback."""
    if snapshot is None or not spec.gate_class:
        return _run_gate_subprocess(spec)
    if spec.owner == "adg_gates":
        return _run_canonical_gate_in_process(spec, snapshot)
    return _run_gate_in_process(spec, snapshot)


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
        # W3 residuals (2026-04-23)
        "B2_layer_skip_ratchet": "wiring_layer_skip_ratchet.json",
        "Q2_cyclomatic_complexity_ratchet": "wiring_cyclomatic_complexity_ratchet.json",
        # W4 semantic-edge ratchets (2026-04-23)
        "C3_silent_writes_ratchet": "wiring_silent_writes_ratchet.json",
        "C4_policy_without_audit_ratchet": "wiring_policy_without_audit_ratchet.json",
        "C5_unresolved_callsites_ratchet": "wiring_unresolved_callsites_ratchet.json",
        "I1_exit_disposition_ratchet": "wiring_exit_disposition_ratchet.json",
        "I2_replay_surface_gaps_ratchet": "wiring_replay_surface_gaps_ratchet.json",
        "O_tool_call_parity_ratchet": "wiring_tool_call_parity_ratchet.json",
        "N_guardrail_separation_ratchet": "wiring_guardrail_separation_ratchet.json",
        # W5 dataflow ratchets (2026-04-23)
        "M_taint_actionable_ratchet": "wiring_taint_actionable_ratchet.json",
        "P_structured_output_ratchet": "wiring_structured_output_ratchet.json",
        "F1_untyped_seam_ratchet": "wiring_untyped_seam_ratchet.json",
        "F2_broken_contract_ratchet": "wiring_broken_contract_ratchet.json",
        # W6 temporal ratchets (2026-04-23)
        "H1_new_orphans_delta_ratchet": "wiring_new_orphans_delta_ratchet.json",
        "H2_fanin_collapse_ratchet": "wiring_fanin_collapse_ratchet.json",
        "H4_mv_staleness_ratchet": "wiring_mv_staleness_ratchet.json",
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
    """Derive human-friendly status using (enforcement, baseline, count).

    H5: canonical gates (owner='adg_gates') carry their own internal ratchet
    (``ADGGateBase._compute_ratchet`` mutates the baseline json on disk), so
    the gate's exit_code is authoritative — no external baseline file lookup.
    Wiring gates (owner='wiring_ci') still need external baseline comparison.
    """
    enf = row["enforcement"]
    count = row["violation_count"]
    if row.get("owner") == "adg_gates":
        row["baseline_count"] = None  # baseline is internal to ADGGateBase
        if enf == "block":
            if row["exit_code"] == 0:
                return "pass"
            return "blocked"
        if enf == "ratchet":
            if row["exit_code"] == 0:
                return "pass"
            return "regressed"
        return "pass"  # warn
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

    # H4: resolve the snapshot ONCE for the whole fleet. In-process gates
    # accept a pre-resolved ``snapshot`` so the dispatcher doesn't pay the
    # glob/mtime scan cost 13 times. Falls back to per-gate resolution inside
    # ``latest_snapshot()`` if this fails.
    snapshot: Path | None = None
    try:
        from ops_scripts.ci._adg_wiring_gate_base import latest_snapshot  # noqa: E402

        snapshot = latest_snapshot()
    except (FileNotFoundError, ImportError, OSError):
        snapshot = None

    # H5: fleet now covers CANONICAL_GATES (13, ADGGateBase) + WIRING_GATES (13, WiringGate).
    # VALIDATION_GATES remain pipeline-phase gates inside generate_full_adg.py
    # and are not dispatched here.
    fleet: list[GateSpec] = [*CANONICAL_GATES, *WIRING_GATES]

    rows: list[dict[str, Any]] = []
    overall_exit = 0
    for spec in tqdm(fleet, desc="ADG gates", unit="gate"):
        row = _run_gate(spec, snapshot=snapshot)
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
        "snapshot": snapshot.name if snapshot else None,
        "snapshot_path": str(snapshot) if snapshot else None,
        "total_gates": len(rows),
        "overall_exit_code": overall_exit,
        "summary": {
            "block_pass": sum(
                1 for r in rows if r["enforcement"] == "block" and r["classification"] == "pass"
            ),
            "block_fail": sum(
                1 for r in rows if r["enforcement"] == "block" and r["classification"] == "blocked"
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

    # Mandatory burndown markdown when burndown table exists from a prior/full ADG run.
    try:
        from tools.reports.adg_burndown_report import emit_mandatory_adg_burndown_report  # noqa: PLC0415

        emit_mandatory_adg_burndown_report(gate_results=json_path, fail_closed=False)
    except ImportError:
        pass

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
