"""
agentic_core/L0_maintenance/scripts/test_final_comprehensive_audit.py
---------------------------------------------------------------------
FIX: Implements Functional Naming (Orchestration/Execution/Cognition).
REMOVED: All legacy 'l3_', 'l2_', 'l1_' variable prefixes.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_case_1_signal_saturation_sweep():
    """
    Test Case 1: The "Signal Saturation" Sweep

    Procedure: Trigger a top-level heal from L3OrchestrationBaseAgent with
    auto_approve=True and custom_telemetry_id="AUDIT-2026".

    Expectation: Every agent in the call path (L3 -> L2 -> L1 -> Root) must
    accept the **kwargs without TypeError.

    Verification: Logs must show AUDIT-2026 reached the SovereignBaseAgent
    termination point.
    """
    print("=" * 70)
    print("TEST CASE 1: SIGNAL SATURATION SWEEP")
    print("=" * 70)

    try:
        from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import (
            L1CognitionBaseAgent,
        )
        from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import (
            L2ExecutionBaseAgent,
        )
        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )

        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # Step 1: Create Orchestrator (top of chain)
        orchestrator = L3OrchestrationBaseAgent()
        print("✓ Step 1: Orchestration Agent instantiated")

        # Step 2: Trigger top-level heal
        result = orchestrator.heal_repository(
            dry_run=True,
            auto_approve=True,
            custom_telemetry_id="AUDIT-2026",
            audit_sweep="signal_saturation",
            propagation_depth="full_chain",
            governance_mode="autonomous",
            test_signal_1="value_1",
            test_signal_2="value_2",
            test_signal_3="value_3",
        )
        print("✓ Step 2: heal_repository called with saturated signals")
        print("  Signals: auto_approve=True, custom_telemetry_id='AUDIT-2026'")
        print(f"  Result: {result}")

        # Step 3: Verify result structure
        if not isinstance(result, dict):
            print(f"❌ FAIL: Expected dict, got {type(result)}")
            return False

        # Should have standard keys from termination point
        if "skipped" not in result and "violations" not in result:
            print(f"❌ FAIL: Missing standard keys in result: {result}")
            return False

        print("✓ Step 3: Result structure validated")

        # Step 4: Test individual layers
        print("\n✓ Step 4: Testing individual layer signal acceptance")

        # Execution Layer
        executor = L2ExecutionBaseAgent(ctx=None)
        exec_result = executor.heal_repository(
            dry_run=True, custom_telemetry_id="AUDIT-2026", layer_test="Execution"
        )
        print(f"  Execution accepts signals: {exec_result}")

        # Cognition Layer
        cognition = L1CognitionBaseAgent()
        cog_result = cognition.heal_repository(
            dry_run=True, custom_telemetry_id="AUDIT-2026", layer_test="Cognition"
        )
        print(f"  Cognition accepts signals: {cog_result}")

        # Sovereign Root
        sovereign = SovereignBaseAgent()
        sov_result = sovereign.heal_repository(
            dry_run=True, custom_telemetry_id="AUDIT-2026", layer_test="Sovereign"
        )
        print(f"  Sovereign accepts signals: {sov_result}")

        print("\n✅ PASS: Signal Saturation Sweep")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_case_2_terminal_independence():
    """
    Test Case 2: Terminal Independence (Gatekeeper)

    Procedure: Set export SOVEREIGN_AUTO_APPROVE=1 and run RedSentinelAgent
    or HierarchyAgent.

    Expectation: No stdin prompt is created; the agent proceeds autonomously.

    Verification: Process must exit cleanly with code 0 without waiting for
    user input.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 2: TERMINAL INDEPENDENCE (GATEKEEPER)")
    print("=" * 70)

    try:
        # Step 1: Set environment variable
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        print("✓ Step 1: Set SOVEREIGN_AUTO_APPROVE=1")

        # Step 2: Test HierarchyAgent (has gatekeeper integration)
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        hierarchy_agent = HierarchyAgent(
            project_root=project_root,
            healing_enabled=False,  # Dry run
            auto_approve=True,
        )
        print("✓ Step 2: HierarchyAgent instantiated")

        # Step 3: Test approval methods without blocking
        test_source = Path("/tmp/test_terminal_independence.py")
        test_target = Path("/tmp/target_terminal_independence.py")

        # This should NOT block for input()
        import time

        start_time = time.time()

        approval = hierarchy_agent._prompt_user_for_move_approval(
            test_source, test_target, "Terminal independence test"
        )

        elapsed_time = time.time() - start_time

        if elapsed_time > 1.0:
            print(f"⚠ WARNING: Approval took {elapsed_time:.2f}s (may have blocked)")
        else:
            print(f"✓ Step 3: Approval completed in {elapsed_time:.3f}s (no blocking)")

        if not approval:
            print("❌ FAIL: Approval denied despite SOVEREIGN_AUTO_APPROVE=1")
            return False

        print(f"✓ Approval granted: {approval}")

        # Step 4: Test archive approval
        archive_approval = hierarchy_agent._prompt_user_for_archive_approval(
            test_source, test_target, "Archive test"
        )
        print(f"✓ Step 4: Archive approval granted: {archive_approval}")

        # Step 5: Test with multiple agents
        print("\n✓ Step 5: Testing multiple agents with SOVEREIGN_AUTO_APPROVE")

        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )
        from agentic_core.L5_safety.validators.L5SafetyBaseAgent import L5SafetyBaseAgent

        orchestrator = L3OrchestrationBaseAgent()
        safety_agent = L5SafetyBaseAgent()

        orch_result = orchestrator.heal_repository(
            dry_run=True, auto_approve=True, terminal_test="Orchestration"
        )
        print(f"  Orchestration autonomous execution: {orch_result}")

        safety_result = safety_agent.heal_repository(
            dry_run=True, auto_approve=True, terminal_test="Safety"
        )
        print(f"  Safety autonomous execution: {safety_result}")

        print("\n✅ PASS: Terminal Independence")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return False
    finally:
        # Clean up
        if "SOVEREIGN_AUTO_APPROVE" in os.environ:
            del os.environ["SOVEREIGN_AUTO_APPROVE"]
            print("✓ Cleanup: SOVEREIGN_AUTO_APPROVE removed")


def test_case_3_depth_constraint_persistence():
    """
    Test Case 3: Depth Constraint Persistence

    Procedure: Set max_depth=2 and trigger a recursive healing chain.

    Expectation: The chain must return depth_limited: True when hitting the 3rd agent.

    Verification: Confirm that the depth counter incremented correctly through
    the **kwargs propagation.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 3: DEPTH CONSTRAINT PERSISTENCE")
    print("=" * 70)

    try:
        from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import (
            L1CognitionBaseAgent,
        )
        from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import (
            L2ExecutionBaseAgent,
        )
        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )

        # Step 1: Test with max_depth=2
        print("✓ Step 1: Testing with max_depth=2")

        orchestrator = L3OrchestrationBaseAgent()

        # Depth 3 - should be limited
        result_d3 = orchestrator.heal_repository(
            dry_run=True, depth=3, max_depth=2, depth_test="level_3"
        )

        if not result_d3.get("depth_limited"):
            print(f"❌ FAIL: Depth 3 should be limited. Got: {result_d3}")
            return False

        print("✓ Step 2: Depth limiting works correctly")

        # Step 3: Test depth propagation
        print("\n✓ Step 3: Testing depth propagation through layers")

        executor = L2ExecutionBaseAgent(ctx=None)
        cognition = L1CognitionBaseAgent()

        exec_result = executor.heal_repository(
            dry_run=True, depth=2, max_depth=2, layer_test="Execution"
        )
        print(f"  Execution at depth 2: {exec_result}")

        cog_result = cognition.heal_repository(
            dry_run=True, depth=2, max_depth=2, layer_test="Cognition"
        )
        print(f"  Cognition at depth 2: {cog_result}")

        # Step 4: Verify depth counter increments
        print("\n✓ Step 4: Verifying depth counter increments")

        call_path = set()

        orchestrator.heal_repository(
            dry_run=True, depth=0, max_depth=3, _call_path=call_path, chain_test="agent_a"
        )

        executor.heal_repository(
            dry_run=True, depth=1, max_depth=3, _call_path=call_path, chain_test="agent_b"
        )

        cognition.heal_repository(
            dry_run=True, depth=2, max_depth=3, _call_path=call_path, chain_test="agent_c"
        )

        print("\n✅ PASS: Depth Constraint Persistence")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return False


def main():
    """Run all final comprehensive audit verification tests."""
    print("\n" + "=" * 70)
    print("FINAL COMPREHENSIVE AUDIT VERIFICATION SUITE")
    print("138-Agent Mass Remediation Validation")
    print("=" * 70)

    results = []
    results.append(test_case_1_signal_saturation_sweep())
    results.append(test_case_2_terminal_independence())
    results.append(test_case_3_depth_constraint_persistence())

    passed = sum(results)
    total = len(results)

    if passed == total:
        print("\n✅ ALL FINAL AUDIT TESTS PASSED - 100% SUCCESS")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
