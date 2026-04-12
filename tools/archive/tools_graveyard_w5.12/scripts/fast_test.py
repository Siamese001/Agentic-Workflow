#!/usr/bin/env python3
"""
Fast test runner — Python-first wrapper for rapid local testing.

Usage:
    python fast_test.py                    # Run all tests (fast mode)
    python fast_test.py unit               # Run unit tests only
    python fast_test.py -k test_name       # Run specific test pattern
    python fast_test.py --lf               # Re-run last failures
    python fast_test.py --adg              # ADG-scoped tests (changed files only)
    python fast_test.py --adg --dry-run    # Show ADG scope without running

Environment:
    FAST_TEST_VERBOSE=1    # Enable verbose output
    FAST_TEST_NO_PARALLEL=1  # Disable parallel execution
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
PYTEST_FAST_INI = REPO_ROOT / "pytest_fast.ini"


def main() -> int:
    import os

    args = sys.argv[1:]

    # Handle ADG-scoped testing
    if "--adg" in args:
        args.remove("--adg")
        dry_run = "--dry-run" in args
        if dry_run:
            args.remove("--dry-run")

        # Get test selection from ADG
        selector_cmd = [
            sys.executable,
            "-m",
            "tools.adg.adg_test_selector",
            "--from-diff",
        ]

        if dry_run:
            print("ADG test selection (dry-run):")
            result = subprocess.run(selector_cmd, cwd=REPO_ROOT)
            return result.returncode

        selector_cmd.append("--pytest-args")
        result = subprocess.run(
            selector_cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"ADG test selector failed: {result.stderr}", file=sys.stderr)
            return result.returncode

        test_files = result.stdout.strip().split()
        if not test_files:
            print("No tests selected by ADG (no changes detected)")
            return 0

        args.extend(test_files)

    # Build pytest command
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        str(PYTEST_FAST_INI),
    ]

    # Add verbosity if requested
    if os.getenv("FAST_TEST_VERBOSE"):
        pytest_cmd.append("-vv")

    # Disable parallel if requested
    if os.getenv("FAST_TEST_NO_PARALLEL"):
        pytest_cmd.extend(["-n", "0"])

    # Add user args
    pytest_cmd.extend(args)

    # Run pytest
    print(f"Running: {' '.join(pytest_cmd)}")
    result = subprocess.run(pytest_cmd, cwd=REPO_ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
