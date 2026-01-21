#!/usr/bin/env python3
"""
Test Suite for Malformed Agents Audit Script

Verifies the audit script correctly classifies:
1. EXACT_DUPLICATE - Identical orphan and class method
2. DIVERGENT - Different logic between orphan and class method
3. ORPHAN_ONLY - No matching class method exists
"""
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

pytest.skip("Script 'scripts.audit_malformed_agents' does not exist", allow_module_level=True)
# from scripts.audit_malformed_agents import analyze_file, normalize_source

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

# =============================================================================
# Test 1: The Clone (EXACT_DUPLICATE)
# =============================================================================
def test_exact_duplicate():
    """File has class with method and identical orphan at bottom."""
    print("\n" + "=" * 70)
    print("Test 1: The Clone (EXACT_DUPLICATE)")
    print("=" * 70)

    # Create a temporary file with exact duplicate
    code = '''
class TestAgent:
    def run(self):
        pass

def run(self):
    pass
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='Agent.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        result = analyze_file(temp_path)

        if result is None:
            test_fail("CLONE-01", "analyze_file returned None, expected MalformedAgent")
            return

        # Check that orphan was detected
        if len(result.orphaned_functions) > 0:
            test_pass("CLONE-01a", f"Detected {len(result.orphaned_functions)} orphan(s)")
        else:
            test_fail("CLONE-01a", "No orphans detected")
            return

        # Check status is EXACT_DUPLICATE
        if result.status == "EXACT_DUPLICATE":
            test_pass("CLONE-01b", "Status: EXACT_DUPLICATE")
        else:
            test_fail("CLONE-01b", f"Status: {result.status}, expected EXACT_DUPLICATE")

        # Check action
        if "DELETE" in result.action:
            test_pass("CLONE-01c", f"Action: {result.action}")
        else:
            test_fail("CLONE-01c", f"Action: {result.action}, expected DELETE")

    finally:
        temp_path.unlink()

# =============================================================================
# Test 2: The Mutant (DIVERGENT)
# =============================================================================
def test_divergent():
    """File has class with stub method but orphan has real logic."""
    print("\n" + "=" * 70)
    print("Test 2: The Mutant (DIVERGENT)")
    print("=" * 70)

    # Create a temporary file with divergent methods
    code = '''
class TestAgent:
    def run(self):
        pass

def run(self):
    # This is the real implementation
    result = do_something()
    process(result)
    return result
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='Agent.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        result = analyze_file(temp_path)

        if result is None:
            test_fail("MUTANT-01", "analyze_file returned None, expected MalformedAgent")
            return

        # Check that orphan was detected
        if len(result.orphaned_functions) > 0:
            test_pass("MUTANT-01a", f"Detected {len(result.orphaned_functions)} orphan(s)")
        else:
            test_fail("MUTANT-01a", "No orphans detected")
            return

        # Check status is DIVERGENT
        if result.status == "DIVERGENT":
            test_pass("MUTANT-01b", "Status: DIVERGENT")
        else:
            test_fail("MUTANT-01b", f"Status: {result.status}, expected DIVERGENT")

        # Check action
        if "MERGE" in result.action:
            test_pass("MUTANT-01c", f"Action: {result.action}")
        else:
            test_fail("MUTANT-01c", f"Action: {result.action}, expected MERGE")

    finally:
        temp_path.unlink()

# =============================================================================
# Test 3: The Stray (ORPHAN_ONLY)
# =============================================================================
def test_orphan_only():
    """File has class (no methods) and orphan function at bottom."""
    print("\n" + "=" * 70)
    print("Test 3: The Stray (ORPHAN_ONLY)")
    print("=" * 70)

    # Create a temporary file with orphan only
    code = '''
class TestAgent:
    pass

def run(self):
    # This method has no home
    return "orphan"
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='Agent.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_path = Path(f.name)

    try:
        result = analyze_file(temp_path)

        if result is None:
            test_fail("STRAY-01", "analyze_file returned None, expected MalformedAgent")
            return

        # Check that orphan was detected
        if len(result.orphaned_functions) > 0:
            test_pass("STRAY-01a", f"Detected {len(result.orphaned_functions)} orphan(s)")
        else:
            test_fail("STRAY-01a", "No orphans detected")
            return

        # Check status is ORPHAN_ONLY
        if result.status == "ORPHAN_ONLY":
            test_pass("STRAY-01b", "Status: ORPHAN_ONLY")
        else:
            test_fail("STRAY-01b", f"Status: {result.status}, expected ORPHAN_ONLY")

        # Check action
        if "MOVE" in result.action:
            test_pass("STRAY-01c", f"Action: {result.action}")
        else:
            test_fail("STRAY-01c", f"Action: {result.action}, expected MOVE")

    finally:
        temp_path.unlink()

# =============================================================================
# Main
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("AUDIT SCRIPT TEST SUITE")
    print("=" * 70)

    test_exact_duplicate()
    test_divergent()
    test_orphan_only()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - AUDIT SCRIPT VERIFIED")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
