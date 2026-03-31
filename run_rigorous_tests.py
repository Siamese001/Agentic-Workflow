#!/usr/bin/env python3
"""
Comprehensive Rigorous Testing Runner
Runs all rigorous tests individually to avoid timeout issues
"""

import subprocess
import sys
import time


def run_test_class(test_class_name, timeout=30):
    """Run a single test class with timeout."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"tests/infrastructure/test_hardening_rigorous.py::{test_class_name}",
        "-v",
        "--tb=short",
        "--disable-warnings",
        f"--timeout={timeout}",
    ]

    print(f"\n{'=' * 60}")
    print(f"Running {test_class_name}")
    print(f"{'=' * 60}")

    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        end_time = time.time()

        print(f"Time: {end_time - start_time:.2f}s")
        print(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)

        return result.returncode == 0

    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ TIMEOUT after {timeout}s")
        return False
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all rigorous test classes."""
    test_classes = [
        "TestEdgeCasesAndBoundaries",
        "TestFailureScenarios",
        "TestConcurrentOperations",
        "TestMemoryAndResourceLeaks",
        "TestSecurityVulnerabilities",
        "TestPerformanceRegression",
        "TestChaosEngineering",
    ]

    print("🚀 Starting Comprehensive Rigorous Testing")
    print(f"Running {len(test_classes)} test classes...")

    results = {}
    total_passed = 0
    total_failed = 0

    for test_class in test_classes:
        passed = run_test_class(test_class)
        results[test_class] = passed

        if passed:
            total_passed += 1
        else:
            total_failed += 1

    # Summary
    print(f"\n{'=' * 60}")
    print("🏁 COMPREHENSIVE TESTING SUMMARY")
    print(f"{'=' * 60}")

    for test_class, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_class:<30} {status}")

    print(f"\nTotal: {len(test_classes)} tests")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {total_passed / len(test_classes) * 100:.1f}%")

    if total_failed == 0:
        print("\n🎉 ALL RIGOROUS TESTS PASSED!")
        print("Infrastructure hardening is production-ready!")
    else:
        print(f"\n⚠️  {total_failed} test classes failed")
        print("Review failed tests before production deployment")

    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
