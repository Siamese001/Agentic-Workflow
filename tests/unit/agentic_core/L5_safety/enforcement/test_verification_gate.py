#!/usr/bin/env python3
"""
Test script for Verification Gate functionality.

This script tests the Epistemic Cascade prevention mechanism
by simulating scenarios where agents might hallucinate fixes.
"""

import tempfile
from pathlib import Path

from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate
from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent
from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)


def test_verification_gate_basic():
    """Test basic verification gate functionality."""
    print("=== Testing Verification Gate Basic Functionality ===")

    gate = VerificationGate()

    # Test with non-existent file
    assert not gate.verify_action(Path("nonexistent.py"), "delete_import", "requests")
    print("✓ Correctly rejected non-existent file")

    # Test with empty file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Empty file\n")
        f.flush()
        temp_path = Path(f.name)

    try:
        # Should fail - no imports in empty file
        assert not gate.verify_action(temp_path, "delete_import", "requests")
        print("✓ Correctly rejected import deletion in empty file")

        # Should fail - no functions in empty file
        assert not gate.verify_action(temp_path, "modify_function", "test_func")
        print("✓ Correctly rejected function modification in empty file")

        # Should fail - no classes in empty file
        assert not gate.verify_action(temp_path, "remove_class", "TestClass")
        print("✓ Correctly rejected class removal in empty file")

    finally:
        temp_path.unlink()


def test_verification_gate_with_real_code():
    """Test verification gate with actual Python code."""
    print("\n=== Testing Verification Gate with Real Code ===")

    gate = VerificationGate()

    # Create test file with imports, functions, and classes
    test_code = '''
import os
import sys
from pathlib import Path

def test_function():
    """Test function."""
    pass

class TestClass:
    """Test class."""

    def test_method(self):
        """Test method."""
        pass

unused_variable = "test"
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # Should succeed - imports exist
        assert gate.verify_action(temp_path, "delete_import", "os")
        assert gate.verify_action(temp_path, "delete_import", "sys")
        assert gate.verify_action(temp_path, "delete_import", "Path")
        print("✓ Correctly verified existing imports")

        # Should fail - import doesn't exist
        assert not gate.verify_action(temp_path, "delete_import", "requests")
        assert not gate.verify_action(temp_path, "delete_import", "nonexistent_module")
        print("✓ Correctly rejected non-existent imports")

        # Should succeed - function exists
        assert gate.verify_action(temp_path, "modify_function", "test_function")
        print("✓ Correctly verified existing function")

        # Should fail - function doesn't exist
        assert not gate.verify_action(temp_path, "modify_function", "nonexistent_function")
        print("✓ Correctly rejected non-existent function")

        # Should succeed - class exists
        assert gate.verify_action(temp_path, "remove_class", "TestClass")
        print("✓ Correctly verified existing class")

        # Should fail - class doesn't exist
        assert not gate.verify_action(temp_path, "remove_class", "NonexistentClass")
        print("✓ Correctly rejected non-existent class")

        # Should succeed - method exists
        assert gate.verify_action(temp_path, "modify_method", "test_method")
        print("✓ Correctly verified existing method")

        # Should fail - method doesn't exist
        assert not gate.verify_action(temp_path, "modify_method", "nonexistent_method")
        print("✓ Correctly rejected non-existent method")

        # Should succeed - variable exists
        assert gate.verify_action(temp_path, "modify_variable", "unused_variable")
        print("✓ Correctly verified existing variable")

        # Should fail - variable doesn't exist
        assert not gate.verify_action(temp_path, "modify_variable", "nonexistent_variable")
        print("✓ Correctly rejected non-existent variable")

    finally:
        temp_path.unlink()


def test_code_healer_integration():
    """Test CodeHealer integration with verification gate."""
    print("\n=== Testing CodeHealer Integration ===")

    # Create test file with unused import
    test_code = '''
import os
import sys  # This import is unused
from pathlib import Path

def test_function():
    """Test function."""
    return os.getcwd()
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        healer = CodeHealerAgent(dry_run=False)

        # Test healing with real unused import - should succeed
        actions = healer.heal_imports(temp_path)
        unused_import_actions = [a for a in actions if "unused import" in a.description]

        print(f"Found {len(unused_import_actions)} unused import actions")
        for action in unused_import_actions:
            print(f"  - {action.description}")

        # Test with hallucinated violation - should be blocked
        violation = ViolationConstraint(
            constraint_type="unused_import",
            severity="warning",
            message="Unused import: nonexistent_module",
            fix_type="delete",
            target_coordinate=ASTCoordinate(line=1, column=0),
            target_node_type="Import",
        )

        import ast

        tree = ast.parse(test_code)
        context = SurgicalContext(
            file_path=temp_path,
            file_content=test_code,
            ast_tree=tree,
            violations=[violation],
            detector_agent="TestAgent",
            detection_method="test",
            violation_id="test_hallucination",
        )

        result = healer.heal_surgical_cst(context)

        if result["status"] == "skipped" and "Hallucination detected" in result["details"]:
            print("✓ Correctly blocked hallucinated fix")
        else:
            print(f"✗ Failed to block hallucinated fix: {result}")

    finally:
        temp_path.unlink()


def test_cache_functionality():
    """Test verification gate caching."""
    print("\n=== Testing Cache Functionality ===")

    gate = VerificationGate()

    test_code = "import os\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # First call - should compute and cache
        result1 = gate.verify_action(temp_path, "delete_import", "os")
        stats1 = gate.get_cache_stats()

        # Second call - should use cache
        result2 = gate.verify_action(temp_path, "delete_import", "os")
        stats2 = gate.get_cache_stats()

        assert result1 == result2  # Results should be identical
        assert stats1["cache_size"] == stats2["cache_size"]  # Cache size should be same

        print("✓ Cache functionality working correctly")
        print(f"  Cache size: {stats1['cache_size']}")

        # Clear cache and verify
        gate.clear_cache()
        stats3 = gate.get_cache_stats()
        assert stats3["cache_size"] == 0
        print("✓ Cache clear functionality working")

    finally:
        temp_path.unlink()


if __name__ == "__main__":
    print("Testing Verification Gate - Epistemic Cascade Prevention")
    print("=" * 60)

    try:
        test_verification_gate_basic()
        test_verification_gate_with_real_code()
        test_code_healer_integration()
        test_cache_functionality()

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Verification Gate is working correctly.")
        print("✅ Epistemic Cascade prevention is active.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
