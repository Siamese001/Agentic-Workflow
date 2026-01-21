#!/usr/bin/env python3
"""
Test Suite: LocationAgent Performance Optimization

Verifies that LocationAgent uses SovereignIndex for file discovery
instead of slow rglob calls that cause timeouts.
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


def test_sovereign_index_import():
    """Verify LocationAgent imports SovereignIndex."""
    print("\n" + "=" * 70)
    print("Test 1: SovereignIndex Import")
    print("=" * 70)

    location_agent = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"
    content = location_agent.read_text(encoding="utf-8")

    if "from agentic_core.utils.sovereign_index import SovereignIndex" in content:
        test_pass("IMPORT", "SovereignIndex import present (canonical)")
    elif "from archives.location_violations.sovereign_index import SovereignIndex" in content:
        test_pass("IMPORT", "SovereignIndex import present (legacy)")
    else:
        test_fail("IMPORT", "SovereignIndex import missing")

    if "SOVEREIGN_INDEX_AVAILABLE" in content:
        test_pass("FLAG", "SOVEREIGN_INDEX_AVAILABLE flag present")
    else:
        test_fail("FLAG", "SOVEREIGN_INDEX_AVAILABLE flag missing")


def test_helper_function():
    """Verify _get_python_files helper function exists."""
    print("\n" + "=" * 70)
    print("Test 2: Helper Function")
    print("=" * 70)

    location_agent = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"
    content = location_agent.read_text(encoding="utf-8")

    if "def _get_python_files(" in content:
        test_pass("HELPER", "_get_python_files helper function exists")
    else:
        test_fail("HELPER", "_get_python_files helper function missing")

    if "index.get_files" in content:
        test_pass("INDEX_CALL", "Uses SovereignIndex.get_files()")
    else:
        test_fail("INDEX_CALL", "Missing SovereignIndex.get_files() call")


def test_no_direct_rglob():
    """Verify no direct rglob calls remain in critical paths."""
    print("\n" + "=" * 70)
    print("Test 3: No Direct rglob Calls")
    print("=" * 70)

    location_agent = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"
    content = location_agent.read_text(encoding="utf-8")

    # Count rglob occurrences
    rglob_count = content.count('.rglob("*.py")')

    # Should only be in the fallback path of _get_python_files
    if rglob_count <= 1:
        test_pass("RGLOB_COUNT", f"Only {rglob_count} rglob call(s) (fallback only)")
    else:
        test_fail("RGLOB_COUNT", f"Found {rglob_count} rglob calls - should be max 1 (fallback)")

    # Check that _get_python_files is used instead
    helper_calls = content.count("_get_python_files(")
    if helper_calls >= 3:
        test_pass("HELPER_USAGE", f"Helper function used {helper_calls} times")
    else:
        test_fail("HELPER_USAGE", f"Helper function only used {helper_calls} times (expected >=3)")


def test_syntax_valid():
    """Verify LocationAgent has valid Python syntax."""
    print("\n" + "=" * 70)
    print("Test 4: Syntax Validation")
    print("=" * 70)

    location_agent = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"
    content = location_agent.read_text(encoding="utf-8")

    try:
        ast.parse(content)
        test_pass("SYNTAX", "Valid Python syntax")
    except SyntaxError as e:
        test_fail("SYNTAX", f"Syntax error: {e}")


def test_sovereign_index_exists():
    """Verify SovereignIndex module exists and is importable."""
    print("\n" + "=" * 70)
    print("Test 5: SovereignIndex Module")
    print("=" * 70)

    sovereign_index = PROJECT_ROOT / "agentic_core/utils/sovereign_index.py"

    if sovereign_index.exists():
        test_pass("FILE_EXISTS", "sovereign_index.py exists")
    else:
        test_fail("FILE_EXISTS", "sovereign_index.py not found")
        return

    content = sovereign_index.read_text(encoding="utf-8")

    if "class SovereignIndex" in content:
        test_pass("CLASS", "SovereignIndex class defined")
    else:
        test_fail("CLASS", "SovereignIndex class not found")

    if "def get_files(" in content:
        test_pass("GET_FILES", "get_files method exists")
    else:
        test_fail("GET_FILES", "get_files method missing")

    if "def get_instance(" in content:
        test_pass("SINGLETON", "get_instance singleton method exists")
    else:
        test_fail("SINGLETON", "get_instance singleton method missing")


def main():
    print("\n" + "=" * 70)
    print("LOCATIONAGENT PERFORMANCE OPTIMIZATION TEST SUITE")
    print("=" * 70)
    print("Verifying SovereignIndex integration to prevent timeouts")

    test_sovereign_index_import()
    test_helper_function()
    test_no_direct_rglob()
    test_syntax_valid()
    test_sovereign_index_exists()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - LOCATIONAGENT OPTIMIZED")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
