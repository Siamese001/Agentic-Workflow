#!/usr/bin/env python3
"""
test_code_standards_enforcer.py - Phase 4 Code Standards Enforcer Test Suite

Tests:
1. Inheritance Audit: Verify layer base class inheritance violations
2. Pattern Violation Test: Mutable defaults, None comparisons, etc.
3. Type Hint Completeness: Missing return/parameter type hints
4. Combined Report: All violations in a single unified report

Usage:
    python scripts/test_code_standards_enforcer.py
    python scripts/test_code_standards_enforcer.py --inheritance-only
    python scripts/test_code_standards_enforcer.py --patterns-only
    python scripts/test_code_standards_enforcer.py --types-only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_self_tests() -> dict[str, Any]:
    """Run the CodeStandardsEnforcerAgent's internal self-tests."""
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        get_code_standards_enforcer,
    )

    enforcer = get_code_standards_enforcer(PROJECT_ROOT)
    return enforcer._run_self_tests()


def test_inheritance_audit() -> dict[str, Any]:
    """
    Inheritance Audit Test: Verify layer base class inheritance violations.

    Creates a class in L2_execution that does not inherit from L2ExecutionBaseAgent.
    Verifies the Unified Enforcer flags the inheritance violation.
    """
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        get_code_standards_enforcer,
    )

    # Use the test fixtures
    fixtures_dir = PROJECT_ROOT / "tests" / "code_standards_fixtures"
    inheritance_file = fixtures_dir / "inheritance_violation.py"

    if not inheritance_file.exists():
        return {"status": "SKIP", "reason": f"Test fixture not found: {inheritance_file}"}

    enforcer = get_code_standards_enforcer(PROJECT_ROOT)

    # Manually set the file path to simulate L2_execution location
    enforcer.violations = []
    enforcer.current_file = str(fixtures_dir / "L2_execution" / "inheritance_violation.py")

    # Parse and visit the file
    import ast

    with open(inheritance_file, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    enforcer.visit(tree)

    # Check for inheritance violations
    inheritance_violations = [
        v for v in enforcer.violations if v.violation_type == "INHERITANCE_ERR"
    ]

    return {
        "status": "PASS" if len(inheritance_violations) >= 1 else "FAIL",
        "violations_found": len(inheritance_violations),
        "details": [{"class": v.message, "line": v.line_number} for v in inheritance_violations],
    }


def test_pattern_violations() -> dict[str, Any]:
    """
    Pattern Violation Test: Verify coding pattern detection.

    Tests:
    - Mutable default arguments (Key 26)
    - None comparisons with == (Key 34)
    - Float equality comparisons (Key 33)
    - Shadowed builtins (Key 36)
    """
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        get_code_standards_enforcer,
    )

    fixtures_dir = PROJECT_ROOT / "tests" / "code_standards_fixtures"
    pattern_file = fixtures_dir / "pattern_violations.py"

    if not pattern_file.exists():
        return {"status": "SKIP", "reason": f"Test fixture not found: {pattern_file}"}

    enforcer = get_code_standards_enforcer(PROJECT_ROOT)

    # Validate the specific file
    results = enforcer.validate_repository(targets=[pattern_file])

    # Count violations by canon key
    pattern_violations = [v for v in results["details"] if v["type"] == "PATTERN_VIOLATION"]

    key_26_count = sum(1 for v in pattern_violations if v.get("canon_key") == 26)
    key_34_count = sum(1 for v in pattern_violations if v.get("canon_key") == 34)
    key_33_count = sum(1 for v in pattern_violations if v.get("canon_key") == 33)
    key_36_count = sum(1 for v in pattern_violations if v.get("canon_key") == 36)

    # Expected: 2 mutable defaults (list/dict literals - set() is a call, not literal)
    # 2 None comparisons, 1 float comparison, 2 shadowed builtins
    expected = {
        "key_26": 2,  # Mutable defaults (list, dict literals only)
        "key_34": 2,  # None comparisons
        "key_33": 1,  # Float comparison
        "key_36": 2,  # Shadowed builtins
    }

    actual = {
        "key_26": key_26_count,
        "key_34": key_34_count,
        "key_33": key_33_count,
        "key_36": key_36_count,
    }

    all_match = all(actual[k] >= expected[k] for k in expected)

    return {
        "status": "PASS" if all_match else "FAIL",
        "total_pattern_violations": len(pattern_violations),
        "expected": expected,
        "actual": actual,
        "details": pattern_violations[:10],  # First 10 for brevity
    }


def test_type_hint_completeness() -> dict[str, Any]:
    """
    Type Hint Completeness Test: Verify missing type hint detection.

    Tests:
    - Missing return type hints
    - Missing parameter type hints
    - Combined report with other violations
    """
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        get_code_standards_enforcer,
    )

    fixtures_dir = PROJECT_ROOT / "tests" / "code_standards_fixtures"
    type_file = fixtures_dir / "type_hint_violations.py"

    if not type_file.exists():
        return {"status": "SKIP", "reason": f"Test fixture not found: {type_file}"}

    enforcer = get_code_standards_enforcer(PROJECT_ROOT)

    # Validate the specific file
    results = enforcer.validate_repository(targets=[type_file])

    # Count type hint violations
    type_violations = [v for v in results["details"] if v["type"] == "TYPE_HINT_ERR"]

    # Count by type
    return_type_missing = sum(1 for v in type_violations if "return type" in v["message"].lower())
    param_type_missing = sum(
        1
        for v in type_violations
        if "parameter" in v["message"].lower() or "argument" in v["message"].lower()
    )

    # We expect at least some violations
    has_violations = len(type_violations) > 0

    return {
        "status": "PASS" if has_violations else "FAIL",
        "total_type_violations": len(type_violations),
        "return_type_missing": return_type_missing,
        "param_type_missing": param_type_missing,
        "details": type_violations[:10],
    }


def test_combined_report() -> dict[str, Any]:
    """
    Combined Report Test: Verify all violations appear in a single unified report.

    Validates that inheritance, pattern, and type hint violations are all
    reported together with consistent JSON schema.
    """
    from agentic_core.L5_safety.validators.CodeStandardsEnforcerAgent import (
        get_code_standards_enforcer,
    )

    fixtures_dir = PROJECT_ROOT / "tests" / "code_standards_fixtures"

    if not fixtures_dir.exists():
        return {"status": "SKIP", "reason": f"Test fixtures directory not found: {fixtures_dir}"}

    # Get all fixture files
    fixture_files = list(fixtures_dir.glob("*.py"))
    fixture_files = [f for f in fixture_files if f.name != "__init__.py"]

    if not fixture_files:
        return {"status": "SKIP", "reason": "No fixture files found"}

    enforcer = get_code_standards_enforcer(PROJECT_ROOT)

    # Validate all fixture files
    results = enforcer.validate_repository(targets=fixture_files)

    # Verify report structure
    required_keys = ["summary", "details", "status"]
    has_required_keys = all(k in results for k in required_keys)

    # Verify summary structure
    summary_keys = [
        "files_scanned",
        "total_violations",
        "inheritance_errors",
        "pattern_violations",
        "type_hint_errors",
    ]
    has_summary_keys = all(k in results.get("summary", {}) for k in summary_keys)

    # Verify violation schema
    valid_schema = True
    for v in results.get("details", []):
        if not all(k in v for k in ["file", "line", "type", "message"]):
            valid_schema = False
            break

    return {
        "status": "PASS" if has_required_keys and has_summary_keys and valid_schema else "FAIL",
        "has_required_keys": has_required_keys,
        "has_summary_keys": has_summary_keys,
        "valid_violation_schema": valid_schema,
        "summary": results.get("summary", {}),
    }


def main():
    parser = argparse.ArgumentParser(description="Test CodeStandardsEnforcerAgent")
    parser.add_argument("--self-test", action="store_true", help="Run only self-tests")
    parser.add_argument("--inheritance-only", action="store_true", help="Run only inheritance test")
    parser.add_argument("--patterns-only", action="store_true", help="Run only pattern test")
    parser.add_argument("--types-only", action="store_true", help="Run only type hint test")
    parser.add_argument("--output-dir", type=str, default="test_results", help="Output directory")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("CodeStandardsEnforcerAgent Test Suite (Phase 4)")
    print("=" * 60)

    results = {
        "timestamp": timestamp,
        "tests": {},
    }

    all_passed = True
    run_all = not any([args.self_test, args.inheritance_only, args.patterns_only, args.types_only])

    # Self-tests
    if args.self_test or run_all:
        print("\n[1/5] Running self-tests...")
        try:
            self_test_results = run_self_tests()
            results["tests"]["self_tests"] = self_test_results
            passed = self_test_results.get("passed", 0)
            failed = self_test_results.get("failed", 0)
            print(f"  ✓ Self-tests: {passed} passed, {failed} failed")
            if failed > 0:
                all_passed = False
        except Exception as e:
            print(f"  ✗ Self-tests failed: {e}")
            results["tests"]["self_tests"] = {"error": str(e)}
            all_passed = False

    # Inheritance audit
    if args.inheritance_only or run_all:
        print("\n[2/5] Running inheritance audit test...")
        try:
            inheritance_results = test_inheritance_audit()
            results["tests"]["inheritance_audit"] = inheritance_results

            if inheritance_results.get("status") == "PASS":
                print(
                    f"  ✓ Inheritance audit PASSED: {inheritance_results.get('violations_found')} violations detected"
                )
            elif inheritance_results.get("status") == "SKIP":
                print(f"  ⊘ Inheritance audit SKIPPED: {inheritance_results.get('reason')}")
            else:
                print("  ✗ Inheritance audit FAILED")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Inheritance audit failed: {e}")
            results["tests"]["inheritance_audit"] = {"error": str(e)}
            all_passed = False

    # Pattern violations
    if args.patterns_only or run_all:
        print("\n[3/5] Running pattern violation test...")
        try:
            pattern_results = test_pattern_violations()
            results["tests"]["pattern_violations"] = pattern_results

            if pattern_results.get("status") == "PASS":
                print(
                    f"  ✓ Pattern violations PASSED: {pattern_results.get('total_pattern_violations')} violations"
                )
                print(f"    Key 26 (mutable defaults): {pattern_results['actual']['key_26']}")
                print(f"    Key 34 (None comparison): {pattern_results['actual']['key_34']}")
                print(f"    Key 33 (float equality): {pattern_results['actual']['key_33']}")
                print(f"    Key 36 (shadowed builtins): {pattern_results['actual']['key_36']}")
            elif pattern_results.get("status") == "SKIP":
                print(f"  ⊘ Pattern violations SKIPPED: {pattern_results.get('reason')}")
            else:
                print("  ✗ Pattern violations FAILED")
                print(f"    Expected: {pattern_results.get('expected')}")
                print(f"    Actual: {pattern_results.get('actual')}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Pattern violation test failed: {e}")
            results["tests"]["pattern_violations"] = {"error": str(e)}
            all_passed = False

    # Type hint completeness
    if args.types_only or run_all:
        print("\n[4/5] Running type hint completeness test...")
        try:
            type_results = test_type_hint_completeness()
            results["tests"]["type_hints"] = type_results

            if type_results.get("status") == "PASS":
                print(
                    f"  ✓ Type hint test PASSED: {type_results.get('total_type_violations')} violations"
                )
                print(f"    Missing return types: {type_results.get('return_type_missing')}")
                print(f"    Missing param types: {type_results.get('param_type_missing')}")
            elif type_results.get("status") == "SKIP":
                print(f"  ⊘ Type hint test SKIPPED: {type_results.get('reason')}")
            else:
                print("  ✗ Type hint test FAILED")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Type hint test failed: {e}")
            results["tests"]["type_hints"] = {"error": str(e)}
            all_passed = False

    # Combined report
    if run_all:
        print("\n[5/5] Running combined report test...")
        try:
            combined_results = test_combined_report()
            results["tests"]["combined_report"] = combined_results

            if combined_results.get("status") == "PASS":
                print("  ✓ Combined report PASSED")
                summary = combined_results.get("summary", {})
                print(f"    Files scanned: {summary.get('files_scanned', 0)}")
                print(f"    Total violations: {summary.get('total_violations', 0)}")
            elif combined_results.get("status") == "SKIP":
                print(f"  ⊘ Combined report SKIPPED: {combined_results.get('reason')}")
            else:
                print("  ✗ Combined report FAILED")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Combined report test failed: {e}")
            results["tests"]["combined_report"] = {"error": str(e)}
            all_passed = False

    # Save results
    output_file = output_dir / f"code_standards_enforcer_test_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")

    if all_passed:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
