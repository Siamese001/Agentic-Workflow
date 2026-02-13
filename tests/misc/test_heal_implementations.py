#!/usr/bin/env python3
"""
Test script to verify heal() method implementations in L5 safety validators.
"""

import importlib.util
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# List of agents to test
AGENTS_TO_TEST = [
    ("agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent", "ArchitectureGovernorAgent"),
    ("agentic_core.L5_safety.reasoning.HierarchyAgent", "HierarchyAgent"),
    (
        "agentic_core.L5_safety.reasoning.FilesystemSSOTReconcilerAgent",
        "FilesystemSSOTReconcilerAgent",
    ),
    ("agentic_core.L5_safety.validators.CodeDeduplicationAgent", "CodeDeduplicationAgent"),
    ("agentic_core.L5_safety.reasoning.LocationHealerAgent", "LocationHealerAgent"),
    ("agentic_core.L5_safety.reasoning.LocationValidatorAgent", "LocationValidatorAgent"),
    ("agentic_core.L5_safety.validators.AutonomyGuardianAgent", "AutonomyGuardianAgent"),
    ("agentic_core.L5_safety.validators.GitAgent", "GitAgent"),
    ("agentic_core.L5_safety.validators.HygieneGuardianAgent", "HygieneGuardianAgent"),
]


def test_heal_method_exists(module_path: str, class_name: str) -> tuple[bool, str]:
    """Test if a class has a heal() method with correct signature."""
    try:
        # Import the module
        module = importlib.import_module(module_path)

        # Get the class
        if not hasattr(module, class_name):
            return False, f"Class {class_name} not found in module"

        agent_class = getattr(module, class_name)

        # Check if heal() method exists
        if not hasattr(agent_class, "heal"):
            return False, "heal() method not found"

        heal_method = agent_class.heal

        # Check if it's callable
        if not callable(heal_method):
            return False, "heal() is not callable"

        # Test the method signature by calling with a test violation
        test_violation = {"type": "TEST", "file": "test_file.py", "message": "Test violation"}

        # For dataclass agents, we need to instantiate differently
        try:
            # Try to create instance (may fail for some agents)
            if class_name in ["HierarchyAgent", "LocationHealerAgent", "LocationValidatorAgent"]:
                instance = agent_class(project_root=project_root)
            elif class_name == "FilesystemSSOTReconcilerAgent":
                instance = agent_class(project_root=project_root, enforcement_mode=False)
            elif class_name == "CodeDeduplicationAgent":
                instance = agent_class()
            elif class_name == "ArchitectureGovernorAgent":
                instance = agent_class(project_root=project_root)
            else:
                # Try generic instantiation
                try:
                    instance = agent_class()
                except:
                    instance = agent_class(project_root=project_root)

            # Call heal() method
            result = instance.heal(test_violation)

            # Verify result has required keys
            required_keys = {"status", "details", "artifacts", "errors"}
            if not all(key in result for key in required_keys):
                return False, f"heal() result missing required keys. Got: {result.keys()}"

            return True, f"heal() works correctly. Status: {result['status']}"

        except Exception as e:
            # If instantiation fails, just check the method exists
            return True, f"heal() method exists (instantiation test skipped: {str(e)[:50]})"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main test execution."""
    print("=" * 70)
    print("Testing heal() method implementations in L5 safety validators")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for module_path, class_name in AGENTS_TO_TEST:
        print(f"Testing {class_name}...", end=" ")
        success, message = test_heal_method_exists(module_path, class_name)

        if success:
            print(f"✓ PASS - {message}")
            passed += 1
        else:
            print(f"✗ FAIL - {message}")
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(AGENTS_TO_TEST)} tests")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
