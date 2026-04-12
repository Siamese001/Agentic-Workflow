#!/usr/bin/env python3
"""
Pre-commit hook for validation enforcement.
"""

import subprocess
import sys


def main():
    """Run validation before commit."""
    # Only run on Python files
    changed_files = []
    try:
        # Get staged files
        result = subprocess.run(
            [
                "git",
                "diff",
                "--cached",
                "--name-only",
                "--diff-filter=ACM",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            changed_files = [
                f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f.startswith("tests/")
            ]
    except Exception:
        pass

    if not changed_files:
        print("No test files changed, skipping validation")
        return 0

    print(f"Validating {len(changed_files)} changed test files...")

    # Run validation
    try:
        result = subprocess.run(
            [
                sys.executable,
                "tools/validation_runner.py",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("ERROR: Validation failed!")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print("Commit blocked due to validation issues.")
            return result.returncode
        else:
            print("SUCCESS: Validation passed!")
            return 0

    except Exception as e:
        print(f"ERROR: Validation error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
