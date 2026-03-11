#!/usr/bin/env python3
"""
V15 P0 Gate Runner - CI-ready single command smoke test

Executes the complete Phase-0 evidence-only pipeline:
1) Regenerates gap analysis from baseline
2) Runs P0 gate on regenerated artifact
3) Exits non-zero on any failure

Usage:
    python ops_scripts/ci/run_v15_p0_gate.py
    python ops_scripts/ci/run_v15_p0_gate.py --baseline custom.json --output out.json

Exit codes:
    0 - P0 gate PASSED
    1 - P0 gate FAILED or error occurred
"""

import sys
import tempfile
from pathlib import Path
from typing import NoReturn
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(PROJECT_ROOT))


def run_subprocess(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run subprocess and return (exit_code, stdout, stderr)."""
    import subprocess

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        return result.returncode, result.stdout, result.stderr
    # guardian: allow-silent-swallow
    except Exception as e:
        raise
        return 1, "", str(e)


def main() -> NoReturn:
    """Execute the complete P0 gate pipeline."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="V15 P0 Gate Runner")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "v15_gap_analysis.json",
        help="Baseline gap JSON path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for regenerated artifact (default: temp file)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output from regeneration and scoreboard",
    )
    args = parser.parse_args()

    # Check for synthetic failure mode (for testing)
    synthetic_fail = os.environ.get("V15_P0_SYNTHETIC_FAIL", "").lower() in ("1", "true", "yes")

    # Validate baseline exists
    if not args.baseline.exists():
        print(f"ERROR: Baseline not found: {args.baseline}", file=sys.stderr)
        sys.exit(1)

    # Use temp file if no output specified
    use_temp = args.output is None
    if use_temp:
        temp_fd, temp_path = tempfile.mkstemp(suffix=".json", prefix="v15_p0_")
        args.output = Path(temp_path)
        import os

        os.close(temp_fd)

    try:
        # Step 1: Regenerate P0 artifact
        print("[REGEN] Regenerating P0 artifact...", file=sys.stderr)
        regen_cmd = [
            sys.executable,
            "ops_scripts/ci/gap_regenerate_p0.py",
            "--baseline",
            str(args.baseline),
            "--out",
            str(args.output),
            "--evidence-log",
        ]
        regen_code, regen_out, regen_err = run_subprocess(regen_cmd, capture=not args.verbose)

        if regen_code != 0:
            print(f"[FAIL] Regeneration failed (exit {regen_code})", file=sys.stderr)
            if not args.verbose:
                print(regen_err, file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(regen_err, file=sys.stderr)  # evidence log goes to stderr

        # Check for synthetic failure mode
        if synthetic_fail:
            print("[FAIL] Synthetic failure mode triggered", file=sys.stderr)
            sys.exit(1)

        # Step 2: Run P0 gate on regenerated artifact
        print("[GATE] Running P0 gate...", file=sys.stderr)
        gate_cmd = [
            sys.executable,
            "ops_scripts/ci/coverage_scoreboard.py",
            "--gap-json",
            str(args.output),
            "--phase",
            "P0",
        ]
        gate_code, gate_out, gate_err = run_subprocess(gate_cmd, capture=not args.verbose)

        if args.verbose:
            print(gate_out, file=sys.stdout)
            if gate_err:
                print(gate_err, file=sys.stderr)

        # Extract result from output
        if not args.verbose:
            # Parse JSON output to get result
            try:
                lines = gate_out.strip().split("\n")
                for line in lines:
                    if line.startswith("PASS:") or line.startswith("FAIL:"):
                        if line.startswith("PASS:"):
                            print("[PASS] P0 gate PASSED", file=sys.stderr)
                            if "source=evidence_only" in line and "evaluated_ids" in line:
                                print(f"      {line.strip()}", file=sys.stderr)
                            sys.exit(0)
                        else:
                            print("[FAIL] P0 gate FAILED", file=sys.stderr)
                            print(f"      {line.strip()}", file=sys.stderr)
                            sys.exit(1)
                # If we didn't find PASS/FAIL line, check exit code
                if gate_code == 0:
                    print("[PASS] P0 gate PASSED", file=sys.stderr)
                    sys.exit(0)
                else:
                    print("[FAIL] P0 gate FAILED", file=sys.stderr)
                    sys.exit(1)
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback to exit code
                print(f"Failed to parse gate result: {e}", file=sys.stderr)
                if gate_code == 0:
                    print("[PASS] P0 gate PASSED", file=sys.stderr)
                    sys.exit(0)
                else:
                    print("[FAIL] P0 gate FAILED", file=sys.stderr)
                    sys.exit(1)
        else:
            # Verbose mode: exit based on subprocess exit code
            if gate_code == 0:
                print("[PASS] P0 gate PASSED", file=sys.stderr)
                sys.exit(0)
            else:
                print("[FAIL] P0 gate FAILED", file=sys.stderr)
                sys.exit(1)

    finally:
        # Cleanup temp file
        if use_temp and args.output.exists():
            try:
                args.output.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    main()
