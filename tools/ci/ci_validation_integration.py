#!/usr/bin/env python3
"""
CI integration for validation enforcement.
"""

import subprocess
import sys
from pathlib import Path


def run_validation():
    """Run validation and output CI-friendly results."""
    try:
        # Run validation runner
        result = subprocess.run([
            sys.executable, "tools/validation_runner.py",
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Output results in CI-friendly format
        print("=== Validation Results ===")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Generate GitHub Actions annotation if needed
        if result.returncode != 0:
            print("::error::Validation failed - check report for details")

        return result.returncode

    except Exception as e:
        print(f"::error::Validation runner error: {e}")
        return 1

def main():
    """Main CI integration."""
    exit_code = run_validation()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
