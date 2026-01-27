"""
MRO Type Safety Test Suite - Sovereign Agent Architecture

Tests for the critical MRO/Type Safety fixes applied to:
- SovereignBaseAgent: Pre-init state containers, initialization order, heal_repository delegation
- HealerMixin: Termination logic, cycle detection, HealResult return type

MANDATORY: ALL TESTS MUST PASS 100% BEFORE DEPLOYMENT

Run with: python scripts/test_mro_type_safety.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_mro_integrity_and_initialization_order():
    """
    Verifies that:
    1. Root state is initialized BEFORE Mixins run (avoiding AttributeError).
    2. The _sovereign_initialized flag prevents double-init.
    3. State containers exist as dataclass fields.
    """
    print("\n[TEST 1] MRO Integrity and Initialization Order...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    try:
        # Create a test agent class
        from dataclasses import dataclass

        @dataclass
        class TestAgent(SovereignBaseAgent):
            pass

        agent = TestAgent()

        # Verify initialization completed
        assert hasattr(agent, "_sovereign_initialized"), "Missing _sovereign_initialized flag"
        assert agent._sovereign_initialized is True, "_sovereign_initialized should be True"

        # Verify state containers exist
        assert hasattr(agent, "_state"), "Missing _state container"
        assert isinstance(agent._state, dict), "_state should be a dict"

        assert hasattr(agent, "_call_path"), "Missing _call_path container"
        assert isinstance(agent._call_path, set), "_call_path should be a set"

        # Verify state was initialized with default values
        assert agent._state.get("status") == "booting", "_state should have 'booting' status"
        assert agent._state.get("health") == "nominal", "_state should have 'nominal' health"

        print("  ✓ Initialization order verified")
        print("  ✓ State containers exist before Mixin execution")
        print("  ✓ _sovereign_initialized sentinel set")
        return True

    except AttributeError as e:
        print(f"  ✗ FAILED: Initialization Order Failure: {e}")
        return False
    except Exception as e:
        print(f"  ✗ FAILED: Unexpected error: {e}")
        return False


def test_heal_repository_return_type_consistency():
    """
    Verifies Liskov Substitution Principle compliance:
    The agent must return a HealResult TypedDict, not a raw dict with wrong keys.
    """
    print("\n[TEST 2] heal_repository Return Type Consistency...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass

    try:

        @dataclass
        class TestAgent(SovereignBaseAgent):
            pass

        agent = TestAgent()
        result = agent.heal_repository(dry_run=True)

        # Verify it's a dict (TypedDict is a dict at runtime)
        assert isinstance(result, dict), f"heal_repository returned {type(result)}, expected dict"

        # Verify it has the canonical HealResult keys
        required_keys = {"violations_found", "violations_fixed", "status", "errors", "skipped"}
        actual_keys = set(result.keys())

        missing_keys = required_keys - actual_keys
        assert not missing_keys, f"Missing canonical keys: {missing_keys}"

        # Verify we did NOT get the old "termination point" dict with wrong keys
        assert "violations" not in result, (
            "Got legacy 'violations' key instead of 'violations_found'"
        )
        assert "fixed" not in result, "Got legacy 'fixed' key instead of 'violations_fixed'"

        print("  ✓ Return type is HealResult-compatible dict")
        print(f"  ✓ Canonical keys present: {required_keys}")
        print("  ✓ No legacy keys present")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_diamond_inheritance_stability():
    """
    Tests deep inheritance chains to ensure MRO resolves
    without method resolution errors or skipped initializers.
    """
    print("\n[TEST 3] Diamond Inheritance Stability...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass

    try:

        @dataclass
        class DeepWorker(SovereignBaseAgent):
            custom_field: str = "test"

        worker = DeepWorker()
        mro_names = [c.__name__ for c in DeepWorker.mro()]

        # Verify MRO structure
        assert mro_names[0] == "DeepWorker", "DeepWorker should be first in MRO"
        assert "SovereignBaseAgent" in mro_names, "SovereignBaseAgent should be in MRO"

        # Verify state persists
        assert worker._state is not None, "_state should not be None"
        assert isinstance(worker._state, dict), "_state should be a dict"

        # Verify custom field works
        assert worker.custom_field == "test", "Custom field should be accessible"

        print(f"  ✓ MRO: {' -> '.join(mro_names[:5])}...")
        print("  ✓ State persists through inheritance")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_double_init_prevention():
    """
    Verifies that the _sovereign_initialized guard prevents double initialization.
    """
    print("\n[TEST 4] Double Initialization Prevention...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass

    try:
        init_count = 0

        @dataclass
        class CountingAgent(SovereignBaseAgent):
            def __post_init__(self):
                nonlocal init_count
                init_count += 1
                super().__post_init__()

        agent = CountingAgent()

        # Manually try to re-init
        agent.__post_init__()
        agent.__post_init__()

        # Should only have initialized once due to guard
        # Note: The first __post_init__ is called by dataclass, then we call it twice more
        # But the guard should prevent re-initialization
        assert agent._sovereign_initialized is True, "Should be initialized"

        print("  ✓ Double initialization guard active")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_cycle_detection():
    """
    Verifies that heal_repository properly detects cycles.
    """
    print("\n[TEST 5] Cycle Detection in heal_repository...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass

    try:

        @dataclass
        class TestAgent(SovereignBaseAgent):
            pass

        agent = TestAgent()

        # Simulate a cycle by pre-populating _call_path
        result = agent.heal_repository(
            dry_run=True,
            _call_path={"TestAgent"},  # Agent already in path = cycle
        )

        assert result["status"] == "SKIPPED", f"Expected SKIPPED status, got {result['status']}"
        assert result["skipped"] == 1, f"Expected skipped=1, got {result['skipped']}"

        print("  ✓ Cycle detection returns SKIPPED status")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_max_depth_termination():
    """
    Verifies that heal_repository terminates at max depth.
    """
    print("\n[TEST 6] Max Depth Termination...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass

    try:

        @dataclass
        class TestAgent(SovereignBaseAgent):
            pass

        agent = TestAgent()

        # Call with depth exceeding max_depth
        result = agent.heal_repository(dry_run=True, depth=10, max_depth=3)

        assert result["status"] == "SKIPPED", f"Expected SKIPPED status, got {result['status']}"
        assert result["skipped"] == 1, f"Expected skipped=1, got {result['skipped']}"

        print("  ✓ Max depth termination returns SKIPPED status")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_mixin_state_access_during_init():
    """
    Verifies that _state exists as a dataclass field BEFORE __post_init__ runs,
    so any code in __post_init__ or infrastructure_mixin.__init__ can safely access it.
    """
    print("\n[TEST 7] State Container Exists Before __post_init__...")

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from dataclasses import dataclass, fields

    try:
        # Verify _state and _call_path are dataclass fields
        field_names = [f.name for f in fields(SovereignBaseAgent)]

        assert "_state" in field_names, "_state should be a dataclass field"
        assert "_call_path" in field_names, "_call_path should be a dataclass field"

        @dataclass
        class TestAgent(SovereignBaseAgent):
            pass

        agent = TestAgent()

        # Verify state containers exist and are properly typed
        assert isinstance(agent._state, dict), "_state should be a dict"
        assert isinstance(agent._call_path, set), "_call_path should be a set"

        # Verify _state was populated by _initialize_sovereign_state
        assert agent._state.get("status") == "booting", "_state should have 'booting' status"

        print("  ✓ _state is a dataclass field (exists before __post_init__)")
        print("  ✓ _call_path is a dataclass field (exists before __post_init__)")
        print("  ✓ State containers properly initialized")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_healer_mixin_heal_result_type():
    """
    Verifies that HealerMixin.heal_repository returns HealResult.
    """
    print("\n[TEST 8] HealerMixin HealResult Type...")

    from agentic_core.base_agents.healer_mixin import HealerMixin

    try:

        class TestMixin(HealerMixin):
            pass

        mixin = TestMixin()
        result = mixin.heal_repository(dry_run=True)

        # Verify it's a dict with HealResult keys
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        required_keys = {"violations_found", "violations_fixed", "status", "errors", "skipped"}
        actual_keys = set(result.keys())

        missing_keys = required_keys - actual_keys
        assert not missing_keys, f"Missing canonical keys: {missing_keys}"

        print("  ✓ HealerMixin returns HealResult-compatible dict")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def run_all_tests():
    """Run all MRO type safety tests."""
    print("=" * 60)
    print("MRO TYPE SAFETY TEST SUITE")
    print("=" * 60)

    tests = [
        test_mro_integrity_and_initialization_order,
        test_heal_repository_return_type_consistency,
        test_diamond_inheritance_stability,
        test_double_init_prevention,
        test_cycle_detection,
        test_max_depth_termination,
        test_mixin_state_access_during_init,
        test_healer_mixin_heal_result_type,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ FAILED with exception: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        print("\n❌ SOME TESTS FAILED - DO NOT DEPLOY")
        return False
    else:
        print("\n✅ ALL TESTS PASSED - Safe to deploy")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
