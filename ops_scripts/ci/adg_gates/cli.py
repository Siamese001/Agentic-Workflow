"""CLI entry point for ADG CI gates.

Usage:
    python -m ops_scripts.ci.adg_gates list
    python -m ops_scripts.ci.adg_gates run-phase A
    python -m ops_scripts.ci.adg_gates run-gate 1,2,3
    python -m ops_scripts.ci.adg_gates run-all
    python -m ops_scripts.ci.adg_gates status
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ops_scripts.ci.adg_gates import GATE_REGISTRY, get_gate, list_gates, run_all, run_phase
from ops_scripts.ci.adg_gates.gate_base import CI_ARTIFACTS_DIR


def cmd_list() -> int:
    """List all available gates."""
    gates = list_gates()
    print("\nADG CI Gates:")
    print("-" * 60)
    for gate_id in sorted(gates.keys(), key=int):
        info = gates[gate_id]
        print(f"  Gate {gate_id}: {info['family']}")
        print(f"    Phase: {info['phase']} | Severity: {info['severity']}")
        print(f"    Views: {', '.join(info['source_views'][:3])}")
        if len(info["source_views"]) > 3:
            print(f"           ... and {len(info['source_views']) - 3} more")
        print()
    print(f"Total: {len(gates)} gates")
    return 0


def cmd_run_phase(phase: str) -> int:
    """Run all gates in a phase."""
    print(f"\nRunning Phase {phase.upper()} gates...")
    print("-" * 60)

    results = run_phase(phase)

    blocked = []
    warned = []
    passed = []

    for gate_id, result in results.items():
        gate_name = GATE_REGISTRY[gate_id][0].gate_family
        if result.status == "blocked":
            blocked.append((gate_id, gate_name, len(result.violations)))
            print(f"  Gate {gate_id} [{gate_name}]: BLOCKED ({len(result.violations)} violations)")
        elif result.status == "warn":
            warned.append((gate_id, gate_name, len(result.violations)))
            print(f"  Gate {gate_id} [{gate_name}]: WARN ({len(result.violations)} violations)")
        else:
            passed.append((gate_id, gate_name))
            print(f"  Gate {gate_id} [{gate_name}]: PASSED")

    print()
    print("-" * 60)
    print(f"Results: {len(passed)} passed, {len(warned)} warned, {len(blocked)} blocked")

    if blocked:
        print("\nBLOCKED gates:")
        for gate_id, gate_name, vcount in blocked:
            print(f"  - Gate {gate_id} [{gate_name}]: {vcount} violations")
        return 1

    return 0


def cmd_run_gate(gate_ids: list[str]) -> int:
    """Run specific gates by ID."""
    print(f"\nRunning gates: {', '.join(gate_ids)}...")
    print("-" * 60)

    blocked = []
    results = {}

    for gate_id in gate_ids:
        gate = get_gate(gate_id)
        if not gate:
            print(f"  Gate {gate_id}: UNKNOWN (skipping)")
            continue

        result = gate.run()
        results[gate_id] = result

        if result.status == "blocked":
            blocked.append((gate_id, gate.gate_family, len(result.violations)))
            print(f"  Gate {gate_id} [{gate.gate_family}]: BLOCKED ({len(result.violations)} violations)")
        elif result.status == "warn":
            print(f"  Gate {gate_id} [{gate.gate_family}]: WARN ({len(result.violations)} violations)")
        else:
            print(f"  Gate {gate_id} [{gate.gate_family}]: PASSED")

    print()
    if blocked:
        print("BLOCKED:")
        for gate_id, name, vcount in blocked:
            print(f"  Gate {gate_id} [{name}]: {vcount} violations")
        return 1

    return 0


def cmd_run_all() -> int:
    """Run all gates."""
    print("\nRunning ALL ADG CI gates...")
    print("=" * 60)

    results = run_all()

    blocked = []
    warned = []
    passed = []

    for gate_id in sorted(results.keys(), key=int):
        result = results[gate_id]
        gate_name = result.gate_family
        if result.status == "blocked":
            blocked.append((gate_id, gate_name, len(result.violations)))
        elif result.status == "warn":
            warned.append((gate_id, gate_name, len(result.violations)))
        else:
            passed.append((gate_id, gate_name))

    print("\nPhase A (P0 Hard-Block):")
    for gate_id in ["1", "2", "3", "4", "5", "6"]:
        if gate_id in results:
            result = results[gate_id]
            symbol = (
                "BLOCKED" if result.status == "blocked" else ("WARN" if result.status == "warn" else "PASS")
            )
            print(f"  Gate {gate_id} [{result.gate_family}]: {symbol}")

    print("\nPhase B (P1 Ratchet):")
    for gate_id in ["7", "8"]:
        if gate_id in results:
            result = results[gate_id]
            symbol = (
                "BLOCKED" if result.status == "blocked" else ("WARN" if result.status == "warn" else "PASS")
            )
            print(f"  Gate {gate_id} [{result.gate_family}]: {symbol}")

    print()
    print("=" * 60)
    print(f"Summary: {len(passed)} passed, {len(warned)} warned, {len(blocked)} blocked")

    if blocked:
        print("\nBLOCKED gates:")
        for gate_id, name, vcount in blocked:
            print(f"  - Gate {gate_id} [{name}]: {vcount} violations")
        print(f"\nArtifacts: {CI_ARTIFACTS_DIR}")
        return 1

    return 0


def cmd_status() -> int:
    """Show current gate baseline and trend status."""
    from ops_scripts.ci.adg_gates.gate_base import CI_RATchet_DIR

    print("\nADG CI Gates Status:")
    print("-" * 60)

    if not CI_RATchet_DIR.exists():
        print("No baselines initialized yet.")
        return 0

    for baseline_file in sorted(CI_RATchet_DIR.glob("*_baseline.json")):
        name = baseline_file.stem.replace("_baseline", "")
        try:
            data = json.loads(baseline_file.read_text(encoding="utf-8"))
            print(f"\n{name}:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"  {key}: {len(value)} entries")
                else:
                    print(f"  {key}: {value}")
        except (OSError, json.JSONDecodeError) as e:
            print(f"  {name}: ERROR ({e})")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ADG Materialized-View-Driven CI Gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ops_scripts.ci.adg_gates list
  python -m ops_scripts.ci.adg_gates run-phase A
  python -m ops_scripts.ci.adg_gates run-gate 1,3,5
  python -m ops_scripts.ci.adg_gates run-all
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list
    subparsers.add_parser("list", help="List all available gates")

    # run-phase
    phase_parser = subparsers.add_parser("run-phase", help="Run all gates in a phase")
    phase_parser.add_argument("phase", choices=["A", "B", "C", "a", "b", "c"], help="Phase to run")

    # run-gate
    gate_parser = subparsers.add_parser("run-gate", help="Run specific gates by ID")
    gate_parser.add_argument("gates", help="Comma-separated gate IDs (e.g., 1,3,5)")

    # run-all
    subparsers.add_parser("run-all", help="Run all gates")

    # status
    subparsers.add_parser("status", help="Show baseline and trend status")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "list":
        return cmd_list()
    elif args.command == "run-phase":
        return cmd_run_phase(args.phase)
    elif args.command == "run-gate":
        gate_ids = [g.strip() for g in args.gates.split(",")]
        return cmd_run_gate(gate_ids)
    elif args.command == "run-all":
        return cmd_run_all()
    elif args.command == "status":
        return cmd_status()

    return 2


if __name__ == "__main__":
    sys.exit(main())
