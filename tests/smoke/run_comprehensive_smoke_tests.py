#!/usr/bin/env python3
"""
Comprehensive smoke test runner.

This script runs ALL smoke tests across ALL domains to ensure complete coverage.
It replaces the phase-based approach to prevent missing directories.

Usage:
    python tests/smoke/run_comprehensive_smoke_tests.py
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result

def main():
    """Run comprehensive smoke tests."""
    print("=" * 80)
    print("COMPREHENSIVE SMOKE TEST SUITE")
    print("=" * 80)
    print("Running ALL smoke tests across ALL domains...")
    print()

    # Run the full smoke test suite
    result = run_command(
        'python -m pytest tests/smoke/ --tb=short -v',
        cwd=Path(__file__).parent.parent.parent
    )

    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Parse results
    for line in result.stdout.split('\n'):
        if '=' in line and ('passed' in line or 'failed' in line or 'skipped' in line):
            print(f"\nRESULT: {line}")

            # Check for failures
            if 'failed' in line and '0 failed' not in line:
                print("\n❌ SMOKE TESTS FAILED!")
                print("Some tests failed. Please fix and re-run.")
                return 1
            else:
                print("\n✅ SMOKE TESTS PASSED!")
                print("All tests either passed or were gracefully skipped.")
                return 0

    print("\n⚠️ Could not determine test results")
    return 1

if __name__ == "__main__":
    sys.exit(main())
