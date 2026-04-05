#!/usr/bin/env python3
"""
Final test suite validation for production readiness.
"""

import subprocess
import sys


def run_final_validation():
    """Run comprehensive final validation."""
    print("=== Final Test Suite Validation ===")

    checks = []

    # 1. Syntax validation
    print("1. Running syntax validation...")
    try:
        result = subprocess.run([
            'python', '-c',
            'import ast; from pathlib import Path; test_dir = Path("tests"); errors = 0; [ast.parse(open(f).read()) for f in test_dir.rglob("test_*.py") if not (ast.parse(open(f).read()) if True else None)]; print("Syntax validation passed")'
        ], capture_output=True, text=True, timeout=300)

        syntax_ok = result.returncode == 0
        checks.append(("Syntax Validation", syntax_ok, result.stdout.strip()))

    except Exception as e:
        checks.append(("Syntax Validation", False, str(e)))

    # 2. Test collection
    print("2. Running test collection...")
    try:
        result = subprocess.run([
            'pytest', '--collect-only', '--quiet', '--tb=no'
        ], capture_output=True, text=True, timeout=300)

        collection_ok = result.returncode == 0 and 'collected' in result.stdout.lower()
        checks.append(("Test Collection", collection_ok, result.stdout.strip()))

    except Exception as e:
        checks.append(("Test Collection", False, str(e)))

    # 3. Smoke tests
    print("3. Running smoke tests...")
    try:
        result = subprocess.run([
            'pytest', 'tests/smoke/', '-v', '--tb=short', '--maxfail=3'
        ], capture_output=True, text=True, timeout=600)

        smoke_ok = result.returncode == 0
        checks.append(("Smoke Tests", smoke_ok, result.stdout.strip()))

    except Exception as e:
        checks.append(("Smoke Tests", False, str(e)))

    # Results
    print("\n=== Validation Results ===")
    all_passed = True
    for check_name, passed, details in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
            print(f"  Details: {details}")

    print(f"\nOverall Status: {'✅ PRODUCTION READY' if all_passed else '❌ NEEDS ATTENTION'}")
    return all_passed


if __name__ == '__main__':
    success = run_final_validation()
    sys.exit(0 if success else 1)
