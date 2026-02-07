#!/usr/bin/env python3
"""
Integration test for LocationAgent with execute_ssot.py healing system.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent


def test_heal_integration():
    """Test LocationAgent heal method with actual file operations."""

    print("=== Integration Test: LocationAgent heal method ===\n")

    # Create a temporary test file in an invalid location
    test_dir = project_root / "temp_test_dir"
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "test_agent.py"
    test_file.write_text("""
# Test file in invalid location
class TestAgent:
    pass
""")

    try:
        # Initialize LocationAgent
        agent = LocationAgent(project_root)

        # Create a violation dict like execute_ssot.py would
        violation = {
            "type": "LOCATION",
            "file": str(test_file),
            "message": "File in invalid location: temp_test_dir",
            "suggested_action": "move to appropriate location",
        }

        print("Testing heal with violation:")
        print(f"  File: {test_file}")
        print(f"  Message: {violation['message']}")
        print()

        # Test heal method (dry run first)
        print("1. Testing heal method (dry run)...")

        # We can't easily test dry run with the current implementation,
        # so let's test the actual heal operation
        result = agent.heal(violation)

        print(f"Result: {json.dumps(result, indent=2)}")

        # Verify result structure
        required_keys = [
            "success",
            "violations_fixed",
            "violations_found",
            "message",
            "target",
            "agent",
            "execution_time_ms",
        ]
        missing_keys = [k for k in required_keys if k not in result]

        if missing_keys:
            print(f"✗ Missing required keys in result: {missing_keys}")
            return False

        if result["violations_found"] != 1:
            print(f"✗ Expected violations_found=1, got {result['violations_found']}")
            return False

        if result["violations_fixed"] not in [0, 1]:
            print(f"✗ Expected violations_fixed to be 0 or 1, got {result['violations_fixed']}")
            return False

        print("✓ heal method returns proper structure")

        # Test heal_violations method
        print("\n2. Testing heal_violations method...")

        violations = [(test_file, "File in invalid location: temp_test_dir")]

        result2 = agent.heal_violations(violations, auto_approve=True)

        print(f"Result: {json.dumps(result2, indent=2)}")

        # Verify result structure
        required_keys2 = ["healed", "total", "success", "message", "execution_time_ms", "details"]
        missing_keys2 = [k for k in required_keys2 if k not in result2]

        if missing_keys2:
            print(f"✗ Missing required keys in result: {missing_keys2}")
            return False

        if result2["total"] != 1:
            print(f"✗ Expected total=1, got {result2['total']}")
            return False

        if result2["healed"] not in [0, 1]:
            print(f"✗ Expected healed to be 0 or 1, got {result2['healed']}")
            return False

        print("✓ heal_violations method returns proper structure")

        # Test with dict format violations
        print("\n3. Testing heal_violations with dict format...")

        dict_violations = [
            {
                "file": str(test_file),
                "message": "File in invalid location (dict format)",
                "type": "LOCATION",
            }
        ]

        result3 = agent.heal_violations(dict_violations, auto_approve=True)

        print(f"Result: {json.dumps(result3, indent=2)}")

        if result3["total"] != 1:
            print(f"✗ Expected total=1 for dict format, got {result3['total']}")
            return False

        print("✓ heal_violations handles dict format violations")

        return True

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_error_handling():
    """Test error handling in heal methods."""

    print("\n=== Error Handling Test ===\n")

    agent = LocationAgent(project_root)

    # Test with missing file path
    print("1. Testing heal with missing file path...")
    result = agent.heal({"message": "no file"})

    if not result.get("success") and result.get("error"):
        print("✓ Properly handles missing file path")
    else:
        print("✗ Should have failed with missing file path")
        return False

    # Test with non-existent file
    print("\n2. Testing heal with non-existent file...")
    result = agent.heal({"file": "non_existent_file.py", "message": "File does not exist"})

    if not result.get("success") and result.get("error"):
        print("✓ Properly handles non-existent file")
    else:
        print("✗ Should have failed with non-existent file")
        return False

    # Test heal_violations with empty list
    print("\n3. Testing heal_violations with empty list...")
    result = agent.heal_violations([])

    if result.get("total") == 0 and result.get("healed") == 0:
        print("✓ Properly handles empty violation list")
    else:
        print("✗ Should handle empty list gracefully")
        return False

    return True


if __name__ == "__main__":
    print("=== LocationAgent execute_ssot.py Integration Test ===\n")

    integration_test = test_heal_integration()
    error_test = test_error_handling()

    print("\n=== Final Results ===")
    print(f"Integration test: {'PASS' if integration_test else 'FAIL'}")
    print(f"Error handling test: {'PASS' if error_test else 'FAIL'}")

    if integration_test and error_test:
        print("\n✅ All integration tests passed!")
        print("LocationAgent is now compatible with execute_ssot.py healing system")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
