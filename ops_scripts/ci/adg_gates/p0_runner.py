"""P0 two-pass runner — preflight then full ADG enforcement.

Implements the explicit P0 gating flow from the execution-policy enhancement:

    Phase A (Preflight):
        1. Run preflight-capable P0 gates on seed graph
        2. If any hit: emit minimal_failure_artifact, classify repairability
        3. If auto_fix_safe and patch generated: rerun preflight on patched tree
        4. If not clean: HALT (exit 1)

    Phase B (Full):
        5. Run all P0 gates on fully-enriched ADG SQLite
        6. If any hit: emit full_adg_report, HALT (exit 1)
        7. If clean: return 0 (allow P1/P2 ratchet evaluation)

Canonical CI truth: ADG SQLite (canonical_policy + sqlite_mv_ci gates only).
GraphDB gates are NOT invoked here — they are derived_explainer only.

Exit codes:
    0 — all P0 gates pass (preflight + full)
    1 — at least one P0 gate blocked
    2 — runner error (missing SQLite, import failure, etc.)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from tqdm import tqdm
except ImportError:
    sys.exit("[FATAL] tqdm not installed — run: pip install tqdm")


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


REPO_ROOT = _bootstrap_repo_root()
CI_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci_gates"

# Lazy imports — gates import SQLite; avoid import-time failures if ADG missing
_GATE_IMPORTS_OK = False
_IMPORT_ERROR: str = ""

try:
    from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult
    from ops_scripts.ci.adg_gates.gate_p0_text_to_action import TextToActionGate
    from ops_scripts.ci.adg_gates.gate_p0_write_sovereignty import WriteSovereigntyGate
    from ops_scripts.ci.adg_gates.gate_p0_authority import AuthorityBoundaryGate
    from ops_scripts.ci.adg_gates.gate_p0_capability_egress import CapabilityEgressGate
    from ops_scripts.ci.adg_gates.gate_p0_critical_path import CriticalPathIntegrityGate as CriticalPathGate
    from ops_scripts.ci.adg_gates.gate_p0_determinism import DeterminismProvenanceGate as DeterminismGate
    from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

    _GATE_IMPORTS_OK = True
except (ImportError, OSError, RuntimeError, TypeError, ValueError) as _exc:
    _IMPORT_ERROR = f"{type(_exc).__name__}: {_exc}"


# ---------------------------------------------------------------------------
# Gate registry — determines which gates run in preflight vs full
# ---------------------------------------------------------------------------

# HITL-2 decision: only text_to_action and write_sovereignty support preflight
PREFLIGHT_GATE_CLASSES = [
    "TextToActionGate",
    "WriteSovereigntyGate",
]

FULL_GATE_CLASSES = [
    "TextToActionGate",
    "WriteSovereigntyGate",
    "AuthorityBoundaryGate",
    "CapabilityEgressGate",
    "CriticalPathGate",
    "DeterminismGate",
]


def _build_gate(
    cls_name: str,
    sqlite_path: Path | None,
    modified_files: list[str],
    preflight_mode: bool,
) -> "ADGGateBase | None":
    """Instantiate a gate by class name. Returns None on import failure."""
    if not _GATE_IMPORTS_OK:
        return None
    mapping: dict[str, type] = {
        "TextToActionGate": TextToActionGate,
        "WriteSovereigntyGate": WriteSovereigntyGate,
        "AuthorityBoundaryGate": AuthorityBoundaryGate,
        "CapabilityEgressGate": CapabilityEgressGate,
        "CriticalPathGate": CriticalPathGate,
        "DeterminismGate": DeterminismGate,
    }
    cls = mapping.get(cls_name)
    if cls is None:
        return None
    return cls(sqlite_path=sqlite_path, modified_files=modified_files, preflight_mode=preflight_mode)


def _write_run_summary(
    phase: str,
    results: list["GateResult"],
    blocked: bool,
    output_dir: Path,
) -> Path:
    """Write a consolidated run summary for the phase."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    summary: dict[str, Any] = {
        "phase": phase,
        "timestamp": ts,
        "blocked": blocked,
        "gate_count": len(results),
        "blocked_gates": [r.gate_family for r in results if r.status == "blocked"],
        "passed_gates": [r.gate_family for r in results if r.status != "blocked"],
        "results": [r.to_dict() for r in results],
    }
    fname = output_dir / f"p0_runner_{phase}_{ts.replace(':', '').replace('.', '_')}.json"
    fname.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return fname


# ---------------------------------------------------------------------------
# Phase A: Preflight
# ---------------------------------------------------------------------------


def run_preflight(
    sqlite_path: Path | None = None,
    modified_files: list[str] | None = None,
    emit_artifacts: bool = True,
) -> tuple[bool, list["GateResult"]]:
    """Run preflight P0 gates on seed graph.

    Returns:
        (all_passed: bool, results: list[GateResult])
        all_passed=True means preflight is clean and Phase B may proceed.
    """
    if not _GATE_IMPORTS_OK:
        print(f"[p0_runner] PREFLIGHT ERROR: gate imports failed — {_IMPORT_ERROR}", file=sys.stderr)
        return False, []

    results: list[GateResult] = []
    any_blocked = False

    for cls_name in tqdm(PREFLIGHT_GATE_CLASSES, desc="Processing", unit="item"):
        gate = _build_gate(cls_name, sqlite_path, modified_files or [], preflight_mode=True)
        if gate is None:
            print(f"[p0_runner] WARNING: could not build gate {cls_name}", file=sys.stderr)
            continue
        try:
            result = gate.run(emit_artifacts=emit_artifacts)
            results.append(result)
            if result.status == "blocked":
                any_blocked = True
                print(
                    f"[p0_runner] PREFLIGHT BLOCKED: {result.gate_family} "
                    f"({len(result.violations)} violations)",
                    file=sys.stderr,
                )
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
            print(
                f"[p0_runner] PREFLIGHT ERROR running {cls_name}: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            any_blocked = True

    if emit_artifacts:
        _write_run_summary("preflight", results, any_blocked, CI_ARTIFACTS_DIR)

    return not any_blocked, results


# ---------------------------------------------------------------------------
# Phase B: Full
# ---------------------------------------------------------------------------


def run_full(
    sqlite_path: Path | None = None,
    modified_files: list[str] | None = None,
    emit_artifacts: bool = True,
) -> tuple[bool, list["GateResult"]]:
    """Run all P0 gates on fully-enriched ADG SQLite.

    Returns:
        (all_passed: bool, results: list[GateResult])
        all_passed=True means all P0 final checks pass.
    """
    if not _GATE_IMPORTS_OK:
        print(f"[p0_runner] FULL ERROR: gate imports failed — {_IMPORT_ERROR}", file=sys.stderr)
        return False, []

    results: list[GateResult] = []
    any_blocked = False

    for cls_name in tqdm(FULL_GATE_CLASSES, desc="Processing", unit="item"):
        gate = _build_gate(cls_name, sqlite_path, modified_files or [], preflight_mode=False)
        if gate is None:
            print(f"[p0_runner] WARNING: could not build gate {cls_name}", file=sys.stderr)
            continue
        try:
            result = gate.run(emit_artifacts=emit_artifacts)
            results.append(result)
            if result.status == "blocked":
                any_blocked = True
                print(
                    f"[p0_runner] FULL BLOCKED: {result.gate_family} ({len(result.violations)} violations)",
                    file=sys.stderr,
                )
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as exc:
            print(f"[p0_runner] FULL ERROR running {cls_name}: {type(exc).__name__}: {exc}", file=sys.stderr)
            any_blocked = True

    if emit_artifacts:
        _write_run_summary("full", results, any_blocked, CI_ARTIFACTS_DIR)

    return not any_blocked, results


# ---------------------------------------------------------------------------
# Orchestrator: Preflight → Full
# ---------------------------------------------------------------------------


def run_p0_two_pass(
    sqlite_path: Path | None = None,
    modified_files: list[str] | None = None,
    emit_artifacts: bool = True,
    skip_preflight: bool = False,
) -> int:
    """Run the complete P0 two-pass flow.

    Args:
        sqlite_path: Path to ADG SQLite. If None, latest is used.
        modified_files: Changed files for modified-area focus.
        emit_artifacts: Write artifacts to artifacts/ci_gates/.
        skip_preflight: Skip Phase A (for testing or when seed graph unavailable).

    Returns:
        0 — all P0 gates pass
        1 — one or more P0 gates blocked
        2 — runner-level error
    """
    if not _GATE_IMPORTS_OK:
        print(f"[p0_runner] FATAL: gate imports failed — {_IMPORT_ERROR}", file=sys.stderr)
        return 2

    # Phase A: Preflight
    if not skip_preflight:
        print("[p0_runner] Phase A: running preflight P0 gates...", file=sys.stderr)
        preflight_passed, preflight_results = run_preflight(
            sqlite_path=sqlite_path,
            modified_files=modified_files,
            emit_artifacts=emit_artifacts,
        )
        if not preflight_passed:
            blocked = [r.gate_family for r in preflight_results if r.status == "blocked"]
            print(
                f"[p0_runner] Phase A FAILED — blocked gates: {blocked}. Full ADG generation halted.",
                file=sys.stderr,
            )
            return 1
        print("[p0_runner] Phase A: preflight clean.", file=sys.stderr)
    else:
        print("[p0_runner] Phase A: preflight skipped (skip_preflight=True).", file=sys.stderr)

    # Phase B: Full
    print("[p0_runner] Phase B: running full P0 gates...", file=sys.stderr)
    full_passed, full_results = run_full(
        sqlite_path=sqlite_path,
        modified_files=modified_files,
        emit_artifacts=emit_artifacts,
    )
    if not full_passed:
        blocked = [r.gate_family for r in full_results if r.status == "blocked"]
        print(
            f"[p0_runner] Phase B FAILED — blocked gates: {blocked}. Merge/baseline promotion halted.",
            file=sys.stderr,
        )
        return 1

    print("[p0_runner] Phase B: full P0 clean. P1/P2 ratchet evaluation may proceed.", file=sys.stderr)
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="P0 two-pass runner (preflight + full)")
    parser.add_argument("--sqlite", type=Path, default=None, help="Path to ADG SQLite")
    parser.add_argument("--modified-files", nargs="*", default=[], help="Changed files")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip Phase A")
    parser.add_argument("--no-artifacts", action="store_true", help="Suppress artifact writes")
    args = parser.parse_args()

    return run_p0_two_pass(
        sqlite_path=args.sqlite,
        modified_files=args.modified_files,
        emit_artifacts=not args.no_artifacts,
        skip_preflight=args.skip_preflight,
    )


if __name__ == "__main__":
    sys.exit(main())
