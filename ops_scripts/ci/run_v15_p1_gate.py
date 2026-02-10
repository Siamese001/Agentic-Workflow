#!/usr/bin/env python3
"""V15 Phase 1 Gate Runner

CI-ready script that runs the Phase 1 gate with proper error handling.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_phase1_gate(repo_root: Path = None) -> int:
    """Run Phase 1 gate and return exit code."""

    # Determine repo root
    if not repo_root:
        repo_root = Path.cwd()

    print("[P1-GATE] Starting Phase 1 gate...")

    # Create temporary file for D-evidence output
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Step 1: Collect D-evidence
        print("[P1-GATE] Collecting D-evidence...")
        evidence_cmd = [
            sys.executable,
            "ops_scripts/ci/v15_d_evidence_collect_p1.py",
            "--repo-root",
            str(repo_root),
            "--output",
            tmp_path,
        ]

        result = subprocess.run(
            evidence_cmd,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        if result.returncode != 0:
            print("[P1-GATE] FAILED: D-evidence collection failed")
            print(result.stderr)
            return result.returncode

        print("[P1-GATE] D-evidence collected successfully")

        # Load evidence to extract key metrics
        with open(tmp_path) as f:
            evidence = json.load(f)

        summary = evidence.get("summary", {})
        critical_passed = summary.get("critical_d_set_passed", False)
        coverage_pct = summary.get("coverage_percentage", 0.0)

        print(f"[P1-GATE] Critical D-set passed: {critical_passed}")
        print(f"[P1-GATE] Coverage: {coverage_pct:.1f}%")

        # Step 2: Run P1 gate with D-evidence
        print("[P1-GATE] Running P1 gate evaluation...")
        gate_cmd = [
            sys.executable,
            "ops_scripts/ci/v15_coverage_scoreboard.py",
            "--phase",
            "P1",
            "--d-evidence",
            tmp_path,
        ]

        result = subprocess.run(
            gate_cmd,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        # Print gate output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("[P1-GATE] PASSED: Phase 1 gate passed")
        else:
            print("[P1-GATE] FAILED: Phase 1 gate failed")

        return result.returncode

    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="V15 Phase 1 Gate Runner")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (default: current directory)",
    )
    args = parser.parse_args()

    return run_phase1_gate(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
