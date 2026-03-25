#!/usr/bin/env python3
"""
Canonical Smoke Test Runner

This is the OFFICIAL smoke test runner that both SWE-1.5 and Opus-4.6 should use.
It ensures consistent test execution across all AI models.

Usage:
    # Run all smoke tests (RECOMMENDED)
    python run_smoke_tests.py

    # Run specific phase
    python run_smoke_tests.py --phase 1
    python run_smoke_tests.py --phase 2
    # etc.

    # Run with additional domains (those not in original phases)
    python run_smoke_tests.py --include-additional
"""

import argparse
import subprocess
import sys
from pathlib import Path

def get_phase_directories(phase):
    """Get directories for a specific phase."""
    from tests.smoke.conftest import PHASE_DEFINITIONS
    return PHASE_DEFINITIONS.get(f'phase{phase}', [])

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

def run_phase_tests(phase, include_additional=False):
    """Run tests for a specific phase."""
    directories = get_phase_directories(phase)
    if not directories:
        print(f"❌ Invalid phase: {phase}")
        return 1

    # Build pytest command
    test_paths = [f"tests/smoke/{d}" for d in directories]

    # Include additional domains if requested
    if include_additional:
        from tests.smoke.conftest import PHASE_DEFINITIONS
        additional_dirs = PHASE_DEFINITIONS.get('additional', [])
        test_paths.extend([f"tests/smoke/{d}" for d in additional_dirs])

    cmd = f'python -m pytest {" ".join(test_paths)} --tb=short -v'

    print(f"\n{'='*80}")
    print(f"RUNNING PHASE {str(phase).upper()} SMOKE TESTS")
    print(f"{'='*80}")
    print(f"Directories: {', '.join(directories)}")
    if include_additional:
        from tests.smoke.conftest import PHASE_DEFINITIONS
        print(f"Additional: {', '.join(PHASE_DEFINITIONS.get('additional', []))}")
    print(f"\nCommand: {cmd}\n")

    result = run_command(cmd)

    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Parse results
    for line in result.stdout.split('\n'):
        if '=' in line and ('passed' in line or 'failed' in line or 'skipped' in line):
            print(f"\nPHASE {str(phase).upper()} RESULT: {line}")

            if 'failed' in line and '0 failed' not in line:
                print(f"\n❌ PHASE {str(phase).upper()} FAILED!")
                return 1
            else:
                print(f"\n✅ PHASE {str(phase).upper()} PASSED!")
                return 0

    print(f"\n⚠️ Could not determine phase {str(phase)} test results")
    return 1

def run_all_tests():
    """Run ALL smoke tests (canonical approach)."""
    cmd = 'python -m pytest tests/smoke/ --tb=short -v'

    print(f"\n{'='*80}")
    print(f"RUNNING ALL SMOKE TESTS (CANONICAL)")
    print(f"{'='*80}")
    print(f"This runs tests from ALL 40 directories")
    print(f"\nCommand: {cmd}\n")

    result = run_command(cmd)

    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Parse results
    for line in result.stdout.split('\n'):
        if '=' in line and ('passed' in line or 'failed' in line or 'skipped' in line):
            print(f"\nOVERALL RESULT: {line}")

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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Canonical Smoke Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_smoke_tests.py              # Run all tests (recommended)
  python run_smoke_tests.py --phase 1    # Run phase 1 only
  python run_smoke_tests.py --phase 2    # Run phase 2 only
  python run_smoke_tests.py --phase 1 --include-additional  # Phase 1 + extra domains
        """
    )

    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help='Run specific phase (1-5)'
    )

    parser.add_argument(
        '--include-additional',
        action='store_true',
        help='Include domains not in original phases (integration, logging, etc.)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.include_additional and not args.phase:
        print("❌ --include-additional requires --phase")
        return 1

    # Run tests
    if args.phase:
        return run_phase_tests(args.phase, args.include_additional)
    else:
        return run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
