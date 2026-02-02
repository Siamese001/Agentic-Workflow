#!/usr/bin/env python3
"""
Test case verifying root hygiene enforcement in structure_blueprint.py
Tests that scripts/ and coverage_html/ are properly blocked while ops_scripts/ is allowed
"""

import sys
from pathlib import Path

# Add the project root to Python path to import the blueprint
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.structure_blueprint_config import is_path_allowed


def test_root_hygiene_enforcement():
    """Test that root hygiene is properly enforced after blueprint changes"""

    print("=== Root Hygiene Enforcement Test ===")

    # Test cases: (path, expected_result, description)
    test_cases = [
        ("scripts/test.py", False, "Root scripts/ should be blocked"),
        ("scripts/maintenance/script.py", False, "Root scripts/ subdirs should be blocked"),
        ("coverage_html/index.html", False, "Root coverage_html/ should be blocked"),
        ("ops_scripts/test.py", True, "ops_scripts/ should be allowed"),
        ("ops_scripts/maintenance/clean.py", True, "ops_scripts/ subdirs should be allowed"),
        ("reports/coverage_html/index.html", True, "reports/coverage_html should be allowed"),
        (
            "agentic_core/L0_maintenance/scripts/test.py",
            True,
            "L0_maintenance/scripts should be allowed",
        ),
        ("agentic_core/base_agents/TestAgent.py", True, "Core agentic paths should be allowed"),
        ("tests/unit/test_something.py", True, "Tests should be allowed"),
        ("docs/readme.md", True, "docs should be allowed"),
    ]

    passed = 0
    failed = 0

    for path, expected, description in test_cases:
        result = is_path_allowed(path)
        status = "✅ PASS" if result == expected else "❌ FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status}: {description}")
        print(f"    Path: '{path}' -> Expected: {expected}, Got: {result}")

    print("\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if failed == 0:
        print("🎉 All tests PASSED! Root hygiene is properly enforced.")
        return True
    else:
        print("💥 Some tests FAILED! Root hygiene violations detected.")
        return False


if __name__ == "__main__":
    success = test_root_hygiene_enforcement()
    sys.exit(0 if success else 1)
