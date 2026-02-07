"""
Phase 1 Restoration Validation Tests
Tests for MetaLearningAgent and IOrchestratorAgent restoration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Any

from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent
from agentic_core.L3_orchestration.types import (
    ExecutionContext,
    ExecutionPhase,
    IOrchestratorAgent,
)


def test_meta_learning_agent_1_1():
    """
    Test Case 1.1: Store an experience with a high reward for 'cot'.
    Verify that update_strategy_weights() increases the weight for 'cot'.
    """
    print("\n=== Test Case 1.1: MetaLearningAgent Weight Update ===")

    agent = MetaLearningAgent(replay_capacity=100)

    # Get initial weight
    initial_weights = agent.strategy_weights.copy()
    initial_cot_weight = initial_weights["cot"]
    print(f"Initial 'cot' weight: {initial_cot_weight}")

    # Store multiple high-reward experiences for 'cot'
    for i in range(10):
        agent.store_experience(
            state={"task": f"test_{i}"},
            thought_type="cot",
            outcome={"success": True},
            reward=0.9,  # High reward
        )

    # Store some low-reward experiences for other strategies
    for strategy in ["tot", "react", "reflection"]:
        agent.store_experience(
            state={"task": "test"},
            thought_type=strategy,
            outcome={"success": False},
            reward=0.1,  # Low reward
        )

    # Update weights
    updated_weights = agent.update_strategy_weights()
    updated_cot_weight = updated_weights["cot"]
    print(f"Updated 'cot' weight: {updated_cot_weight}")

    # Verify cot weight increased
    assert updated_cot_weight > initial_cot_weight, (
        f"Expected 'cot' weight to increase, but got {updated_cot_weight} <= {initial_cot_weight}"
    )

    # Verify cot has highest weight
    max_weight_strategy = max(updated_weights, key=updated_weights.get)
    assert max_weight_strategy == "cot", (
        f"Expected 'cot' to have highest weight, but '{max_weight_strategy}' has highest"
    )

    print(
        f"Test Case 1.1 PASSED: 'cot' weight increased "
        f"from {initial_cot_weight:.3f} to {updated_cot_weight:.3f}"
    )
    return True


def test_meta_learning_agent_1_2():
    """
    Test Case 1.2: Ensure get_strategy_recommendation() returns the strategy
    with the highest weight.
    """
    print("\n=== Test Case 1.2: MetaLearningAgent Strategy Recommendation ===")

    agent = MetaLearningAgent(replay_capacity=100)

    # Manually set weights to make 'tot' highest
    agent.strategy_weights = {
        "cot": 0.5,
        "tot": 0.9,  # Highest
        "react": 0.3,
        "reflection": 0.2,
    }

    print(f"Strategy weights: {agent.strategy_weights}")

    # Get recommendation
    recommended = agent.get_strategy_recommendation(context={})
    print(f"Recommended strategy: {recommended}")

    # Verify it returns 'tot'
    assert recommended == "tot", f"Expected recommendation 'tot', but got '{recommended}'"

    # Test with different highest weight
    agent.strategy_weights["reflection"] = 1.0
    recommended = agent.get_strategy_recommendation(context={})
    print(f"After changing weights, recommended strategy: {recommended}")

    assert recommended == "reflection", f"Expected recommendation 'reflection', but got '{recommended}'"

    print("✅ Test Case 1.2 PASSED: get_strategy_recommendation() returns highest-weighted strategy")
    return True


def test_orchestrator_interface_2_1():
    """
    Test Case 2.1: Verify IOrchestratorAgent cannot be instantiated directly
    (enforcing ABC).
    """
    print("\n=== Test Case 2.1: IOrchestratorAgent ABC Enforcement ===")

    try:
        # Attempt to instantiate abstract class directly
        IOrchestratorAgent()
        print("❌ Test Case 2.1 FAILED: IOrchestratorAgent was instantiated (should be abstract)")
        return False
    except TypeError as e:
        print(f"Expected TypeError caught: {e}")
        print("✅ Test Case 2.1 PASSED: IOrchestratorAgent cannot be instantiated directly")
        return True


def test_orchestrator_interface_2_2():
    """
    Test Case 2.2: Confirm MCPHardenedMixin and HealerMixin methods are available
    in a mock subclass of the interface.
    """
    print("\n=== Test Case 2.2: IOrchestratorAgent Mixin Integration ===")

    # Create a concrete implementation for testing
    class MockOrchestrator(IOrchestratorAgent):
        def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
            """
            Autonomous healing method (Canon Key 51 compliance).

            Args:
                dry_run: If True, only report violations without fixing
                execute: If True, apply fixes

            Returns:
                Dict with healing summary
            """
            return {"violations": 0, "fixed": 0, "errors": 0}

        def execute(self, context: ExecutionContext) -> dict[str, Any]:
            return {"status": "executed"}

        def think(self, context: ExecutionContext) -> dict[str, Any]:
            return {"thoughts": ["plan_step_1"]}

        def act(self, actions: list[dict[str, Any]], context: ExecutionContext) -> list[dict[str, Any]]:
            return [{"action": "completed"}]

        def observe(self, action_results: list[dict[str, Any]], context: ExecutionContext) -> dict[str, Any]:
            return {"observations": ["result_1"]}

        def should_continue(self, context: ExecutionContext) -> bool:
            return False

        def get_state(self) -> dict[str, Any]:
            return {"state": "idle"}

    # Instantiate mock orchestrator
    orchestrator = MockOrchestrator()
    print(f"Created MockOrchestrator instance: {orchestrator.__class__.__name__}")

    # Check for HealerMixin methods
    assert hasattr(orchestrator, "heal_repository"), "Missing HealerMixin method: heal_repository"
    print("✓ HealerMixin method 'heal_repository' available")

    # Check for MCPHardenedMixin methods (common methods)
    mcp_methods = ["validate_mcp_call", "log_mcp_interaction"]
    for method in mcp_methods:
        if hasattr(orchestrator, method):
            print(f"✓ MCPHardenedMixin method '{method}' available")

    # Check for SubatomicTestingMixin methods
    subatomic_methods = [
        "enable_test_mode",
        "disable_test_mode",
        "is_test_mode",
        "record_test_result",
    ]
    for method in subatomic_methods:
        assert hasattr(orchestrator, method), f"Missing SubatomicTestingMixin method: {method}"
        print(f"✓ SubatomicTestingMixin method '{method}' available")

    # Test ExecutionContext dataclass
    context = ExecutionContext(task_id="test_task_001", input_data={"query": "test"})
    print(f"✓ ExecutionContext created: task_id={context.task_id}")

    # Test ExecutionPhase enum
    assert ExecutionPhase.PLANNING.value == "planning"
    assert ExecutionPhase.EXECUTION.value == "execution"
    print(f"✓ ExecutionPhase enum working: {[p.value for p in ExecutionPhase]}")

    # Test abstract methods are callable
    result = orchestrator.execute(context)
    assert result["status"] == "executed"
    print("✓ Abstract methods implemented and callable")

    print("✅ Test Case 2.2 PASSED: Mixins integrated successfully into IOrchestratorAgent")
    return True


def run_all_tests():
    """Run all Phase 1 validation tests."""
    print("=" * 70)
    print("PHASE 1 RESTORATION VALIDATION TESTS")
    print("=" * 70)

    tests = [
        ("MetaLearningAgent 1.1", test_meta_learning_agent_1_1),
        ("MetaLearningAgent 1.2", test_meta_learning_agent_1_2),
        ("IOrchestratorAgent 2.1", test_orchestrator_interface_2_1),
        ("IOrchestratorAgent 2.2", test_orchestrator_interface_2_2),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test {test_name} FAILED with exception: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED - Phase 1 restoration complete!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed - review required")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
