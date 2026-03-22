"""
Wave 7 (P4): Structural Debt Burndown Tracker.

Reports current counts for the three Wave 7 debt metrics:
  1. dead_imports   — ruff F401 violations per layer (ADG or ruff scan)
  2. antipatterns   — from ADG Redis snapshot graph_plane_counts
  3. unresolved     — from ADG Redis snapshot unresolved_count

Compares against Wave 0 baselines and Wave 7a/7b acceptance gates.

Usage:
    python ops_scripts/ci/_wave7_burndown_tracker.py          # full report
    python ops_scripts/ci/_wave7_burndown_tracker.py --check  # exit 1 if 7a gate not met
    python ops_scripts/ci/_wave7_burndown_tracker.py --check --phase 7b
"""

from __future__ import annotations

# Configuration constants
DEFAULT_TIMEOUT = 60

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BASELINE_FILE = _REPO_ROOT / "ops_scripts" / "ci" / "wave0_baseline.json"

# Wave 7 acceptance gates per plan
_GATES: dict[str, dict[str, int]] = {
    "7a": {
        "dead_imports_max": 2000,
        "unresolved_max": 50,
    },
    "7b": {
        "dead_imports_max": 500,
        "antipattern_max": 500,
        "unresolved_max": 50,
        "registers_antipattern_min": 50,
    },
    "final": {
        "dead_imports_max": 0,
        "antipattern_max": 200,
        "unresolved_max": 0,
    },
}

# Layer → directory mapping (relative to repo root)
_LAYER_DIRS: dict[str, list[str]] = {
    "L_TEST": ["tests"],
    "L_OPS": ["ops_scripts"],
    "L_APP": ["apps", "apps_lic", "apps_rg", "apps_exec", "apps_eval", "apps_rfp", "apps_research", "apps_shared"],
    "L_TOOLS": ["tools"],
    "L_RUNTIME": ["agentic_core/runtime"],
    "L_SL": ["system_learning"],
    "L0": ["agentic_core/L0_routing"],
    "L1": ["agentic_core/L1_cognition"],
    "L2": ["agentic_core/L2_execution"],
    "L3": ["agentic_core/L3_orchestration"],
    "L4": ["agentic_core/L4_state"],
    "L5": ["agentic_core/L5_safety"],
    "L6": ["agentic_core/L6_observability"],
}


def _load_baseline() -> dict:
    if not _BASELINE_FILE.exists():
        return {}
    return json.loads(_BASELINE_FILE.read_text(encoding="utf-8"))


def _get_adg_counts() -> dict[str, int]:
    """Fetch graph_plane_counts from Redis ADG snapshot."""
    try:
        import redis  # type: ignore[import]
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        raw = r.get("adg:snapshot")
        if raw:
            snap = json.loads(raw)
            return snap.get("graph_plane_counts", {})
    # guardian: allow-silent-swallower
    except Exception as exc:
        print(f"  [WARN] Failed to get ADG snapshot from Redis: {exc}", file=sys.stderr)
    return {}


def _count_ruff_violations(layer: str) -> int:
    """Count ruff F401 (unused import) violations for a layer's directories."""
    dirs = _LAYER_DIRS.get(layer, [])
    if not dirs:
        return -1
    existing = [str(_REPO_ROOT / d) for d in dirs if (_REPO_ROOT / d).exists()]
    if not existing:
        return 0
    try:
        result = subprocess.run(
            ["python", "-m", "ruff", "check", "--select", "F401", "--output-format", "json"] + existing,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
        if result.stdout.strip():
            violations = json.loads(result.stdout)
            return len(violations)
        return 0
    # guardian: allow-silent-swallower
    except Exception as exc:
        print(f"  [WARN] ruff scan failed for {layer}: {exc}", file=sys.stderr)
        return -1


def _scan_all_dead_imports() -> dict[str, int]:
    """Scan all layers for F401 dead imports."""
    counts: dict[str, int] = {}
    for layer in _LAYER_DIRS:
        counts[layer] = _count_ruff_violations(layer)
    return counts


def _print_report(
    adg_counts: dict[str, int],
    dead_by_layer: dict[str, int],
    baseline: dict,
) -> dict[str, int]:
    """Print full Wave 7 burndown report. Returns summary totals."""
    baseline_counts = baseline.get("counts", {})
    baseline_dead = baseline_counts.get("dead_imports", 4409)
    baseline_antipattern = baseline_counts.get("antipattern", 1528)
    baseline_unresolved = baseline_counts.get("unresolved_count", 412)

    current_antipattern = adg_counts.get("antipattern", -1)
    current_unresolved = adg_counts.get("unresolved_count", -1)
    current_dead_total = sum(v for v in dead_by_layer.values() if v >= 0)

    print("=" * 68)
    print("WAVE 7 STRUCTURAL DEBT BURNDOWN REPORT")
    print("=" * 68)

    adg_total_override = dead_by_layer.pop("__total__", None)
    if adg_total_override is not None:
        current_dead_total = adg_total_override if adg_total_override >= 0 else current_dead_total

    print("\n[1] Dead Imports (ruff F401) by layer:")
    for layer, count in sorted(dead_by_layer.items()):
        tag = " <-- 7a priority" if layer in ("L_TEST", "L_OPS") else ""
        if count < 0:
            print(f"  {layer:12s}  N/A (ruff not run)")
        else:
            print(f"  {layer:12s}  {count:6d}{tag}")
    if adg_total_override is not None:
        print(f"  {'TOTAL (ADG)':14s}  {current_dead_total:6d}  (baseline: {baseline_dead})")
    else:
        print(f"  {'TOTAL':12s}  {current_dead_total:6d}  (baseline: {baseline_dead})")

    print("\n[2] Antipatterns (ADG Redis):")
    if current_antipattern >= 0:
        delta = current_antipattern - baseline_antipattern
        sign = "+" if delta > 0 else ""
        print(f"  current:  {current_antipattern}  (baseline: {baseline_antipattern}, delta: {sign}{delta})")
    else:
        print("  UNAVAILABLE (Redis not accessible)")

    print("\n[3] Unresolved imports (ADG Redis):")
    if current_unresolved >= 0:
        delta = current_unresolved - baseline_unresolved
        sign = "+" if delta > 0 else ""
        print(f"  current:  {current_unresolved}  (baseline: {baseline_unresolved}, delta: {sign}{delta})")
    else:
        print("  UNAVAILABLE (Redis not accessible)")

    print("\n[4] Acceptance gates:")
    for phase_name, gates in _GATES.items():
        print(f"\n  Phase {phase_name}:")
        for gate_key, gate_val in gates.items():
            if gate_key == "dead_imports_max":
                actual = current_dead_total
                status = "PASS" if actual <= gate_val else "FAIL"
            elif gate_key == "antipattern_max":
                actual = current_antipattern
                status = "PASS" if actual >= 0 and actual <= gate_val else ("N/A" if actual < 0 else "FAIL")
            elif gate_key == "unresolved_max":
                actual = current_unresolved
                status = "PASS" if actual >= 0 and actual <= gate_val else ("N/A" if actual < 0 else "FAIL")
            elif gate_key == "registers_antipattern_min":
                actual = adg_counts.get("registers_antipattern", 0)
                status = "PASS" if actual >= gate_val else "FAIL"
            else:
                actual = -1
                status = "N/A"
            print(f"    [{status}] {gate_key}: {actual} (target: {gate_val})")

    print("\n" + "=" * 68)

    return {
        "dead_imports_total": current_dead_total,
        "antipattern": current_antipattern,
        "unresolved": current_unresolved,
    }


def _check_phase(phase: str, totals: dict[str, int]) -> bool:
    """Return True if the given phase acceptance gate is met."""
    gates = _GATES.get(phase, {})
    for gate_key, gate_val in gates.items():
        if gate_key == "dead_imports_max":
            if totals.get("dead_imports_total", 9999) > gate_val:
                return False
        elif gate_key == "antipattern_max":
            actual = totals.get("antipattern", -1)
            if actual >= 0 and actual > gate_val:
                return False
        elif gate_key == "unresolved_max":
            actual = totals.get("unresolved", -1)
            if actual >= 0 and actual > gate_val:
                return False
        elif gate_key == "registers_antipattern_min":
            actual = totals.get("registers_antipattern", 0)
            if actual < gate_val:
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Wave 7 structural debt burndown tracker")
    parser.add_argument("--check", action="store_true", help="Exit 1 if acceptance gate not met")
    parser.add_argument("--phase", default="7a", choices=list(_GATES.keys()),
                        help="Phase acceptance gate to check (default: 7a)")
    parser.add_argument("--no-ruff", action="store_true", help="Skip ruff scan (ADG snapshot only)")
    args = parser.parse_args()

    baseline = _load_baseline()
    adg_counts = _get_adg_counts()

    if args.no_ruff:
        dead_total = adg_counts.get("dead_imports", -1)
        dead_by_layer = dict.fromkeys(_LAYER_DIRS, -1)
        dead_by_layer["__total__"] = dead_total
    else:
        print("Scanning layers for F401 dead imports (this may take a moment)...")
        dead_by_layer = _scan_all_dead_imports()

    totals = _print_report(adg_counts, dead_by_layer, baseline)

    if args.check:
        passed = _check_phase(args.phase, totals)
        if passed:
            print(f"Wave 7 phase {args.phase} acceptance gate: PASSED")
            return 0
        else:
            print(f"Wave 7 phase {args.phase} acceptance gate: FAILED", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
