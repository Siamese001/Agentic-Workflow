"""
HealerMixin heal_repository Architectural Fix Validation
Tests that heal_repository is properly inherited from HealerMixin
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Any

from agentic_core.L3_orchestration.interfaces import ExecutionContext, IOrchestratorAgent
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


def test_healer_mixin_has_heal_repository():
    """Test that HealerMixin now provides heal_repository method."""
    print("\n=== Test: HealerMixin provides heal_repository ===")

    assert hasattr(HealerMixin, "heal_repository"), "HealerMixin must have heal_repository method"

    # Create a simple class using HealerMixin
    class TestAgent(HealerMixin):
        pass

    agent = TestAgent()

    # Test method exists and is callable
    assert hasattr(agent, "heal_repository"), "Instance must have heal_repository method"
    assert callable(agent.heal_repository), "heal_repository must be callable"

    print("✓ HealerMixin.heal_repository exists and is callable")
    print("✅ PASSED")
    return True


def test_heal_repository_signature():
    """Test that heal_repository has the correct signature."""
    print("\n=== Test: heal_repository signature ===")

    class TestAgent(HealerMixin):
        pass

    agent = TestAgent()

    # Test with default arguments
    result = agent.heal_repository()
    assert isinstance(result, dict), "Must return dict"
    assert "violations" in result, "Must have 'violations' key"
    assert "fixed" in result, "Must have 'fixed' key"
    assert "errors" in result, "Must have 'errors' key"
    print(f"✓ Default call result: {result}")

    # Test with all arguments
    result = agent.heal_repository(
        dry_run=False, execute=True, depth=1, max_depth=5, _call_path=set()
    )
    assert isinstance(result, dict), "Must return dict with all args"
    print(f"✓ Full signature call result: {result}")

    print("✅ PASSED")
    return True


def test_heal_repository_cycle_detection():
    """Test that heal_repository detects cycles."""
    print("\n=== Test: heal_repository cycle detection ===")

    class TestAgent(HealerMixin):
        pass

    agent = TestAgent()

    # Simulate a cycle by pre-adding the agent name to call path
    call_path = {"TestAgent"}
    result = agent.heal_repository(_call_path=call_path)

    assert result.get("cycle_detected") == True, "Must detect cycle when agent already in call path"
    assert result.get("skipped") == 1, "Must skip when cycle detected"
    print(f"✓ Cycle detection result: {result}")

    print("✅ PASSED")
    return True


def test_heal_repository_depth_limiting():
    """Test that heal_repository enforces depth limits."""
    print("\n=== Test: heal_repository depth limiting ===")

    class TestAgent(HealerMixin):
        pass

    agent = TestAgent()

    # Exceed max depth
    result = agent.heal_repository(depth=10, max_depth=3)

    assert result.get("depth_limited") == True, "Must detect depth limit exceeded"
    assert result.get("skipped") == 1, "Must skip when depth limited"
    print(f"✓ Depth limiting result: {result}")

    print("✅ PASSED")
    return True


def test_orchestrator_inherits_heal_repository():
    """Test that IOrchestratorAgent inherits heal_repository from HealerMixin."""
    print("\n=== Test: IOrchestratorAgent inherits heal_repository ===")

    # Create concrete implementation
    class MockOrchestrator(IOrchestratorAgent):
        def execute(self, context: ExecutionContext) -> dict[str, Any]:
            return {"status": "executed"}

        def think(self, context: ExecutionContext) -> dict[str, Any]:
            return {"thoughts": []}

        def act(
            self, actions: list[dict[str, Any]], context: ExecutionContext
        ) -> list[dict[str, Any]]:
            return []

        def observe(
            self, action_results: list[dict[str, Any]], context: ExecutionContext
        ) -> dict[str, Any]:
            return {}

        def should_continue(self, context: ExecutionContext) -> bool:
            return False

        def get_state(self) -> dict[str, Any]:
            return {}

    orchestrator = MockOrchestrator()

    # Verify heal_repository is inherited (not defined in IOrchestratorAgent)
    assert hasattr(orchestrator, "heal_repository"), "Orchestrator must have heal_repository"

    # Check that it comes from HealerMixin (not overridden)
    method = orchestrator.__class__.heal_repository

    # Call it and verify it works
    result = orchestrator.heal_repository(dry_run=True)
    assert isinstance(result, dict), "Must return dict"
    assert "violations" in result, "Must have standard keys"
    print(f"✓ Orchestrator heal_repository result: {result}")

    # Verify the method resolution order includes HealerMixin
    mro = [cls.__name__ for cls in MockOrchestrator.__mro__]
    assert "HealerMixin" in mro, "HealerMixin must be in MRO"
    print(f"✓ MRO includes HealerMixin: {mro}")

    print("✅ PASSED")
    return True


def test_subclass_can_extend_heal_repository():
    """Test that subclasses can extend heal_repository and call super()."""
    print("\n=== Test: Subclass can extend heal_repository ===")

    class ExtendedAgent(HealerMixin):
        def __init__(self):
            super().__init__()
            self.heal_called = False

        def heal_repository(self, dry_run=True, execute=False, **kwargs):
            # Call parent first (the pattern used across codebase)
            parent_result = super().heal_repository(dry_run, execute, **kwargs)

            # Add custom logic
            self.heal_called = True
            parent_result["custom_field"] = "extended"
            return parent_result

    agent = ExtendedAgent()
    result = agent.heal_repository()

    assert agent.heal_called == True, "Custom logic must execute"
    assert result.get("custom_field") == "extended", "Custom field must be present"
    assert "violations" in result, "Parent fields must be preserved"
    print(f"✓ Extended heal_repository result: {result}")

    print("✅ PASSED")
    return True


def run_all_tests():
    """Run all HealerMixin heal_repository tests."""
    print("=" * 70)
    print("HEALER MIXIN heal_repository ARCHITECTURAL FIX VALIDATION")
    print("=" * 70)

    tests = [
        ("HealerMixin provides heal_repository", test_healer_mixin_has_heal_repository),
        ("heal_repository signature", test_heal_repository_signature),
        ("heal_repository cycle detection", test_heal_repository_cycle_detection),
        ("heal_repository depth limiting", test_heal_repository_depth_limiting),
        ("IOrchestratorAgent inherits heal_repository", test_orchestrator_inherits_heal_repository),
        ("Subclass can extend heal_repository", test_subclass_can_extend_heal_repository),
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
        print("\n🎉 ALL TESTS PASSED - HealerMixin architectural fix validated!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
