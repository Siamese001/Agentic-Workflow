#!/usr/bin/env python3
"""
Test script to verify ARTIFACT_ROUTING_MAP negative logic implementation.

Validates that forbidden_extensions and forbidden_keywords are properly enforced
by LocationValidatorAgent and HierarchyAgent.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.structure_blueprint import (
    validate_artifact_routing,
    check_forbidden_signals,
)


def test_forbidden_extensions():
    """Test that forbidden extensions are properly rejected."""
    print("\n=== Testing Forbidden Extensions ===")

    test_cases = [
        # (filename, content, should_reject, description)
        ("audit_report.py", "def main():", True, "Python file should be rejected for docs/reports"),
        ("error_log.py", "class ErrorHandler:", True, "Python file should be rejected for logs"),
        ("debug_trace.pyc", None, True, "Compiled Python should be rejected for logs"),
        (
            "audit_results.md",
            "# Assessment Report",
            False,
            "Markdown file should be accepted for docs/reports",
        ),
        (
            "mission_trace.jsonl",
            '{"mission_id": "123"}',
            False,
            "JSONL should be accepted for logs",
        ),
    ]

    passed = 0
    failed = 0

    for filename, content, should_reject, description in test_cases:
        is_valid, dest, rejection = validate_artifact_routing(filename, content)

        if should_reject:
            if not is_valid:
                print(f"✅ PASS: {description}")
                print(f"   Rejected: {rejection}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected rejection but got: is_valid={is_valid}, dest={dest}")
                failed += 1
        else:
            if is_valid:
                print(f"✅ PASS: {description}")
                print(f"   Accepted: dest={dest}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected acceptance but got rejection: {rejection}")
                failed += 1

    print(f"\nForbidden Extensions: {passed} passed, {failed} failed")
    return failed == 0


def test_forbidden_keywords():
    """Test that forbidden keywords are properly rejected."""
    print("\n=== Testing Forbidden Keywords ===")

    test_cases = [
        # (filename, content, should_reject, description)
        ("report.md", "def main():\n    pass", True, "Markdown with 'def ' should be rejected"),
        ("analysis.txt", "class MyClass:", True, "Text file with 'class ' should be rejected"),
        ("script.md", "import sys\nimport os", True, "Markdown with 'import ' should be rejected"),
        ("findings.md", "# Assessment\n## Findings", False, "Clean markdown should be accepted"),
        ("dataset.json", '{"record_count": 100}', False, "Clean JSON should be accepted"),
        (
            "util_script.py",
            "def main():\n    pass",
            False,
            "Python script should be accepted for scripts/",
        ),
    ]

    passed = 0
    failed = 0

    for filename, content, should_reject, description in test_cases:
        is_valid, dest, rejection = validate_artifact_routing(filename, content)

        if should_reject:
            if not is_valid:
                print(f"✅ PASS: {description}")
                print(f"   Rejected: {rejection}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected rejection but got: is_valid={is_valid}, dest={dest}")
                failed += 1
        else:
            if is_valid:
                print(f"✅ PASS: {description}")
                print(f"   Accepted: dest={dest}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected acceptance but got rejection: {rejection}")
                failed += 1

    print(f"\nForbidden Keywords: {passed} passed, {failed} failed")
    return failed == 0


def test_check_forbidden_signals_helper():
    """Test the check_forbidden_signals helper function."""
    print("\n=== Testing check_forbidden_signals Helper ===")

    test_cases = [
        ("report.py", None, True, "Python extension should be forbidden"),
        ("report.md", "def main():", True, "Markdown with code should be forbidden"),
        ("report.md", "# Clean Report", False, "Clean markdown should be allowed"),
        ("data.json", '{"key": "value"}', False, "Clean JSON should be allowed"),
    ]

    passed = 0
    failed = 0

    for filename, content, should_be_forbidden, description in test_cases:
        rejection = check_forbidden_signals(filename, content)

        if should_be_forbidden:
            if rejection:
                print(f"✅ PASS: {description}")
                print(f"   Rejection: {rejection}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print("   Expected rejection but got None")
                failed += 1
        else:
            if not rejection:
                print(f"✅ PASS: {description}")
                passed += 1
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected None but got rejection: {rejection}")
                failed += 1

    print(f"\nHelper Function: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all tests."""
    print("=" * 70)
    print("ARTIFACT ROUTING NEGATIVE LOGIC TEST SUITE")
    print("=" * 70)

    results = []
    results.append(("Forbidden Extensions", test_forbidden_extensions()))
    results.append(("Forbidden Keywords", test_forbidden_keywords()))
    results.append(("Helper Function", test_check_forbidden_signals_helper()))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Negative logic is working correctly!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
