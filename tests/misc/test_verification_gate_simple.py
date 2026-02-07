#!/usr/bin/env python3
"""
Simplified test script for Verification Gate functionality.

This script tests the core verification gate without complex dependencies.
"""

# Import only the verification gate directly
import sys
import tempfile
from pathlib import Path

sys.path.append(".")

from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate


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


def test_hallucination_prevention():
    """Test that verification gate prevents hallucinated fixes."""
    print("\n=== Testing Hallucination Prevention ===")

    gate = VerificationGate()

    # Test file with only one import
    test_code = """
import os

def test_function():
    return os.getcwd()
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # Test trying to delete non-existent import (hallucinated fix)
        result = gate.verify_action(temp_path, "delete_import", "requests")
        assert not result, "Should have blocked hallucinated import deletion"
        print("✓ Correctly blocked hallucinated import deletion")

        # Test trying to modify non-existent function (hallucinated fix)
        result = gate.verify_action(temp_path, "modify_function", "nonexistent_func")
        assert not result, "Should have blocked hallucinated function modification"
        print("✓ Correctly blocked hallucinated function modification")

        # Test trying to remove non-existent class (hallucinated fix)
        result = gate.verify_action(temp_path, "remove_class", "NonexistentClass")
        assert not result, "Should have blocked hallucinated class removal"
        print("✓ Correctly blocked hallucinated class removal")

        print("✅ Epistemic Cascade prevention is working!")

    finally:
        temp_path.unlink()


if __name__ == "__main__":
    print("Testing Verification Gate - Epistemic Cascade Prevention")
    print("=" * 60)

    try:
        test_verification_gate_basic()
        test_verification_gate_with_real_code()
        test_cache_functionality()
        test_hallucination_prevention()

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Verification Gate is working correctly.")
        print("✅ Epistemic Cascade prevention is active.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
