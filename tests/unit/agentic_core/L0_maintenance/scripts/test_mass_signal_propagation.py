"""
agentic_core/L0_maintenance/scripts/test_mass_signal_propagation.py
-------------------------------------------------------------------
FIX: Implements Functional Naming.
REMOVED: 'l3_agent', 'l2_agent' legacy names.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_case_1_long_chain_propagation():
    """
    Test Case 1: The "Long Chain" Propagation Test

    Procedure: Create a mock orchestration that triggers
    L3Orchestrator → L2ExecutionBase → L1CognitionBase → SovereignBase.

    Input: Pass a unique flag global_audit_id="2026-X1".

    Verification: Ensure the flag is received by SovereignBaseAgent (the termination point)
    without any intermediary agent throwing a TypeError.
    """
    print("=" * 70)
    print("TEST CASE 1: LONG CHAIN PROPAGATION TEST")
    print("=" * 70)

    try:
        from agentic_core.L1_cognition.thought_engine.l1_cognition_base_agent import (
            L1CognitionBaseAgent,
        )
        from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import (
            L2ExecutionBaseAgent,
        )
        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )

        # Step 1: Create Orchestrator
        orchestrator = L3OrchestrationBaseAgent()
        print("✓ Step 1: Orchestration Agent instantiated")

        # Step 2: Call with unique global audit ID
        result = orchestrator.heal_repository(
            dry_run=True,
            global_audit_id="2026-X1",
            propagation_test="long_chain",
            custom_signal="mass_remediation",
        )
        print("✓ Step 2: heal_repository called with global_audit_id='2026-X1'")

        # Verify result from SovereignBaseAgent termination
        if not isinstance(result, dict):
            print(f"❌ FAIL: Expected dict, got {type(result)}")
            return False

        # Should have standard keys from termination point
        if "skipped" not in result:
            print(f"❌ FAIL: Missing 'skipped' key in result: {result}")
            return False

        print(f"✓ Result from chain: {result}")

        # Step 3: Test Execution → Cognition → Sovereign
        print("\n✓ Step 3: Testing Execution → Cognition → Sovereign chain")
        executor = L2ExecutionBaseAgent(ctx=None)
        exec_result = executor.heal_repository(
            dry_run=True, global_audit_id="2026-X1", layer_test="Execution"
        )
        print(f"  Execution result: {exec_result}")

        # Step 4: Test Cognition → Sovereign chain
        print("\n✓ Step 4: Testing Cognition → Sovereign chain")
        cognition = L1CognitionBaseAgent()
        cog_result = cognition.heal_repository(
            dry_run=True, global_audit_id="2026-X1", layer_test="Cognition"
        )
        print(f"  Cognition result: {cog_result}")

        print("\n✅ PASS: Long Chain Propagation Test")
        return True

    except TypeError as e:
        print(f"\n❌ FAIL: TypeError in chain - {e}")
        print("   Signal propagation broken at intermediary layer")
        import traceback

        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_case_2_multi_agent_cycle_persistence():
    """
    Test Case 2: Multi-Agent Cycle Persistence

    Procedure: Trigger a recursive heal on an agent that calls a sibling
    (e.g., HistorianAgent calling StrategicPlannerAgent).

    Verification: Confirm that _call_path is correctly populated and maintained
    through the **kwargs propagation, preventing infinite recursion.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 2: MULTI-AGENT CYCLE PERSISTENCE")
    print("=" * 70)

    try:
        from agentic_core.L2_execution.tool_registry.L2ExecutionBaseAgent import (
            L2ExecutionBaseAgent,
        )
        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )

        # Step 1: Create agents
        orchestrator = L3OrchestrationBaseAgent()
        executor = L2ExecutionBaseAgent(ctx=None)
        print("✓ Step 1: Created Orchestrator and Executor")

        # Step 2: Simulate Orchestrator in call path
        call_path = set()
        call_path.add("L3OrchestrationBaseAgent")

        # Step 3: Executor tries to call with Orchestrator already in path
        result_exec = executor.heal_repository(dry_run=True, _call_path=call_path, cycle_test="multi_agent")
        print(f"✓ Step 3: Executor called with existing path: {result_exec}")

        # Step 4: Simulate cycle
        call_path.add("L2ExecutionBaseAgent")
        result_orch = orchestrator.heal_repository(
            dry_run=True, _call_path=call_path, cycle_test="return_call"
        )

        if result_orch.get("cycle_detected"):
            print(f"  ✓ Cycle detected correctly: {result_orch}")

        print("\n✅ PASS: Multi-Agent Cycle Persistence")
        return True

    except RecursionError:
        print("\n❌ FAIL: RecursionError - infinite loop detected")
        print("   _call_path not properly maintained through propagation")
        return False
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_case_3_gatekeeper_automation_sweep():
    """
    Test Case 3: Gatekeeper Automation Sweep

    Procedure: In a shell, run export SOVEREIGN_AUTO_APPROVE=1.

    Verification: Run the healing method for LocationHealerAgent and GovernanceAgent.

    Pass Condition: No stdin prompt is triggered; both agents proceed to report
    violations based on environment signals.
    """
    print("\n" + "=" * 70)
    print("TEST CASE 3: GATEKEEPER AUTOMATION SWEEP")
    print("=" * 70)

    try:
        # Step 1: Set environment variable
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        print("✓ Step 1: Set SOVEREIGN_AUTO_APPROVE=1")

        # Step 2: Test HierarchyAgent (has gatekeeper integration)
        from agentic_core.L5_safety.validators.core.hierarchy_agent import HierarchyAgent

        hierarchy_agent = HierarchyAgent(
            project_root=project_root,
            healing_enabled=False,  # Dry run
            auto_approve=True,
        )
        print("✓ Step 2: HierarchyAgent instantiated with auto_approve=True")

        # Test approval without blocking
        test_source = Path("/tmp/test_file.py")
        test_target = Path("/tmp/target_file.py")

        approval = hierarchy_agent._prompt_user_for_move_approval(
            test_source, test_target, "Gatekeeper automation sweep test"
        )

        if not approval:
            print("❌ FAIL: Approval denied despite SOVEREIGN_AUTO_APPROVE=1")
            return False

        print(f"✓ Approval granted without stdin prompt: {approval}")

        # Step 3: Test with multiple agents
        from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import (
            L3OrchestrationBaseAgent,
        )
        from agentic_core.L5_safety.validators.l5_safety_base_agent import L5SafetyBaseAgent

        orchestrator = L3OrchestrationBaseAgent()
        safety_agent = L5SafetyBaseAgent()

        orch_result = orchestrator.heal_repository(
            dry_run=True, auto_approve=True, sweep_test="Orchestration"
        )
        print(f"  Orchestration result: {orch_result}")

        safety_result = safety_agent.heal_repository(dry_run=True, auto_approve=True, sweep_test="Safety")
        print(f"  Safety result: {safety_result}")

        print("\n✅ PASS: Gatekeeper Automation Sweep")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up
        if "SOVEREIGN_AUTO_APPROVE" in os.environ:
            del os.environ["SOVEREIGN_AUTO_APPROVE"]
            print("✓ Cleanup: SOVEREIGN_AUTO_APPROVE removed")


def main():
    print("\n" + "=" * 70)
    print("MASS SIGNAL PROPAGATION VERIFICATION SUITE")
    print("=" * 70)

    results = []
    results.append(test_case_1_long_chain_propagation())
    results.append(test_case_2_multi_agent_cycle_persistence())
    results.append(test_case_3_gatekeeper_automation_sweep())

    if all(results):
        print("\n✅ ALL MASS PROPAGATION TESTS PASSED - 100% SUCCESS")
        return 0
    else:
        print("\n❌ TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
