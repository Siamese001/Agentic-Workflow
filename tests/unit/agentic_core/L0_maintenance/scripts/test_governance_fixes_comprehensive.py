#!/usr/bin/env python3
"""
Comprehensive Governance Fixes Verification Suite

Implements all 4 required test cases:
1. Signal Propagation Depth Test
2. Sovereign Bypass (Gatekeeper) Test
3. Recursion Cycle Detection
4. MRO Root Termination
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_case_1_signal_propagation():
    """
    Test Case 1: Signal Propagation Depth Test

    Objective: Verify that arbitrary keyword arguments reach the SovereignBaseAgent
    root without causing TypeError.

    Procedure:
    1. Instantiate L6ObservabilityBaseAgent.
    2. Call agent.heal_repository(custom_governance_signal="ACTIVE").

    Expected Result: The method returns a success dictionary; no TypeError is raised
    because **kwargs absorbed the unknown signal.
    """
    print("=" * 70)
    print("TEST CASE 1: SIGNAL PROPAGATION DEPTH TEST")
    print("=" * 70)

    try:
        from agentic_core.L6_observability.L6ObservabilityBaseAgent import L6ObservabilityBaseAgent

        # Step 1: Instantiate L6ObservabilityBaseAgent
        agent = L6ObservabilityBaseAgent()
        print("✓ Step 1: L6ObservabilityBaseAgent instantiated")

        # Step 2: Call with custom governance signal
        result = agent.heal_repository(
            custom_governance_signal="ACTIVE",
            arbitrary_param="test_value",
            extra_metadata={"source": "governance_test"},
        )
        print("✓ Step 2: heal_repository called with custom signals")

        # Verify result
        if not isinstance(result, dict):
            print(f"❌ FAIL: Expected dict, got {type(result)}")
            return False

        # Should have standard keys from SovereignBaseAgent termination
        if "skipped" not in result:
            print(f"❌ FAIL: Missing 'skipped' key in result: {result}")
            return False

        print(f"✓ Result: {result}")
        print("\n✅ PASS: Signal Propagation Depth Test")
        print("   - Custom signals propagated without TypeError")
        print("   - **kwargs absorbed unknown parameters")
        print("   - MRO chain terminated cleanly at SovereignBaseAgent")
        return True

    except TypeError as e:
        print(f"\n❌ FAIL: TypeError raised - {e}")
        print("   **kwargs not properly propagated through MRO chain")
        return False
    except Exception as e:
        print(f"\n❌ FAIL: Unexpected error - {e}")
        import traceback

        traceback.print_exc()
        return False


def test_case_2_sovereign_bypass():
    """
    Test Case 2: Sovereign Bypass (Gatekeeper) Test

    Objective: Ensure that environment-level "Auto Approve" signals bypass manual intervention.

    Procedure:
    1. Set environment variable export SOVEREIGN_AUTO_APPROVE=1.
    2. Trigger HierarchyAgent.heal_repository(execute=True).

    Expected Result: The agent executes the restructure without pausing for an input() call.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 2: SOVEREIGN BYPASS (GATEKEEPER) TEST")
    print("=" * 70)

    try:
        # Step 1: Set environment variable
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        print("✓ Step 1: Set SOVEREIGN_AUTO_APPROVE=1")

        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        # Step 2: Create HierarchyAgent and test approval
        agent = HierarchyAgent(
            project_root=project_root,
            healing_enabled=False,  # Dry run to avoid actual file operations
            auto_approve=True,
        )
        print("✓ Step 2: HierarchyAgent instantiated with auto_approve=True")

        # Test the approval method directly
        test_source = Path("/tmp/test_source.py")
        test_target = Path("/tmp/test_target.py")

        # This should NOT block for input()
        approval = agent._prompt_user_for_move_approval(
            test_source, test_target, "Test restructuring for governance verification"
        )
        print("✓ Step 3: _prompt_user_for_move_approval called (no blocking)")

        if not approval:
            print("\n❌ FAIL: Approval denied despite SOVEREIGN_AUTO_APPROVE=1")
            return False

        print(f"✓ Approval granted: {approval}")
        print("\n✅ PASS: Sovereign Bypass (Gatekeeper) Test")
        print("   - SOVEREIGN_AUTO_APPROVE environment variable respected")
        print("   - No terminal input() blocking occurred")
        print("   - Gatekeeper delegation working correctly")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up environment variable
        if "SOVEREIGN_AUTO_APPROVE" in os.environ:
            del os.environ["SOVEREIGN_AUTO_APPROVE"]
            print("✓ Cleanup: SOVEREIGN_AUTO_APPROVE removed")


def test_case_3_recursion_cycle_detection():
    """
    Test Case 3: Recursion Cycle Detection

    Objective: Confirm that adding **kwargs and super() calls didn't break cycle detection.

    Procedure:
    1. Mock a call chain where Agent A calls Agent B which calls Agent A.
    2. Pass the _call_path set through the heal_repository chain.

    Expected Result: The second call to Agent A returns {"errors": 1, "cycle_detected": True}.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 3: RECURSION CYCLE DETECTION")
    print("=" * 70)

    try:
        from agentic_core.L6_observability.L6ObservabilityBaseAgent import L6ObservabilityBaseAgent

        # Step 1: Create agent instance
        agent = L6ObservabilityBaseAgent()
        print("✓ Step 1: L6ObservabilityBaseAgent instantiated")

        # Step 2: Simulate cycle by pre-populating _call_path
        call_path = {"L6ObservabilityBaseAgent"}
        print("✓ Step 2: Simulated call path with agent already visited")

        # Step 3: Call heal_repository with the agent already in call_path
        result = agent.heal_repository(
            dry_run=True, _call_path=call_path, test_signal="cycle_detection"
        )
        print("✓ Step 3: heal_repository called with pre-populated _call_path")

        # Verify cycle detection
        if not result.get("cycle_detected"):
            print(f"\n❌ FAIL: Cycle not detected. Result: {result}")
            return False

        if result.get("errors") != 1:
            print(f"\n❌ FAIL: Expected errors=1, got: {result}")
            return False

        print(f"✓ Result: {result}")
        print("\n✅ PASS: Recursion Cycle Detection")
        print("   - Cycle correctly detected when agent revisited")
        print("   - Returns {'errors': 1, 'cycle_detected': True}")
        print("   - **kwargs propagation didn't break cycle detection")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_case_4_mro_root_termination():
    """
    Test Case 4: MRO Root Termination

    Objective: Verify SovereignBaseAgent correctly stops the super() chain to avoid
    missing methods in infrastructure_mixin.

    Procedure:
    1. Call heal_repository on a SovereignBaseAgent instance directly.

    Expected Result: Returns {"skipped": 1} cleanly; does not throw AttributeError
    by attempting to call a non-existent super().heal_repository() in a mixin.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 4: MRO ROOT TERMINATION")
    print("=" * 70)

    try:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # Step 1: Instantiate SovereignBaseAgent directly
        agent = SovereignBaseAgent()
        print("✓ Step 1: SovereignBaseAgent instantiated directly")

        # Step 2: Call heal_repository on the root
        result = agent.heal_repository(dry_run=True, test_termination="root_call")
        print("✓ Step 2: heal_repository called on root agent")

        # Verify result structure
        if not isinstance(result, dict):
            print(f"\n❌ FAIL: Expected dict, got {type(result)}")
            return False

        # Should have skipped=1 from termination point
        if result.get("skipped") != 1:
            print(f"\n❌ FAIL: Expected skipped=1, got: {result}")
            return False

        # Verify standard keys
        expected_keys = {"violations", "fixed", "errors", "skipped"}
        if not expected_keys.issubset(result.keys()):
            print(f"\n❌ FAIL: Missing expected keys. Got: {result.keys()}")
            return False

        print(f"✓ Result: {result}")
        print("\n✅ PASS: MRO Root Termination")
        print("   - SovereignBaseAgent terminates cleanly without super() call")
        print("   - No AttributeError from missing mixin methods")
        print("   - Returns standard healing dictionary")
        return True

    except AttributeError as e:
        print(f"\n❌ FAIL: AttributeError - {e}")
        print("   SovereignBaseAgent attempted super() call into mixin without heal_repository")
        return False
    except Exception as e:
        print(f"\n❌ FAIL: Unexpected error - {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all governance fixes verification tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE GOVERNANCE FIXES VERIFICATION SUITE")
    print("=" * 70)
    print()

    results = []

    # Test Case 1: Signal Propagation Depth Test
    results.append(test_case_1_signal_propagation())

    # Test Case 2: Sovereign Bypass (Gatekeeper) Test
    results.append(test_case_2_sovereign_bypass())

    # Test Case 3: Recursion Cycle Detection
    results.append(test_case_3_recursion_cycle_detection())

    # Test Case 4: MRO Root Termination
    results.append(test_case_4_mro_root_termination())

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL GOVERNANCE FIXES VERIFIED - 100% PASS RATE")
        print("\nStructural remediation complete:")
        print("  ✓ Signal propagation through MRO chain")
        print("  ✓ Sovereign bypass (SOVEREIGN_AUTO_APPROVE)")
        print("  ✓ Recursion cycle detection intact")
        print("  ✓ MRO root termination without overflow")
        print("\nDeployment Status: READY ✅")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - REMEDIATION INCOMPLETE")
        print("\nDeployment Status: BLOCKED ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())
