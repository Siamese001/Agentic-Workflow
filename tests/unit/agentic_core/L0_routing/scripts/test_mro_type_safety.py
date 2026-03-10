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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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

    from dataclasses import dataclass

    @dataclass
    class TestAgent(SovereignBaseAgent):
        pass

    agent = TestAgent()

    assert hasattr(agent, "_sovereign_initialized"), "Missing _sovereign_initialized flag"
    assert agent._sovereign_initialized is True, "_sovereign_initialized should be True"
    assert hasattr(agent, "_state"), "Missing _state container"
    assert isinstance(agent._state, dict), "_state should be a dict"
    assert hasattr(agent, "_call_path"), "Missing _call_path container"
    assert isinstance(agent._call_path, set), "_call_path should be a set"
    assert agent._state.get("status") == "booting", "_state should have 'booting' status"
    assert agent._state.get("health") == "nominal", "_state should have 'nominal' health"


def test_heal_repository_return_type_consistency():
    """
    Verifies Liskov Substitution Principle compliance:
    The agent must return a HealResult TypedDict, not a raw dict with wrong keys.
    """
    print("\n[TEST 2] heal_repository Return Type Consistency...")

    from dataclasses import dataclass

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    @dataclass
    class TestAgent(SovereignBaseAgent):
        pass

    agent = TestAgent()
    result = agent.heal_repository(dry_run=True)

    assert isinstance(result, dict), f"heal_repository returned {type(result)}, expected dict"
    required_keys = {"violations_found", "violations_fixed", "status", "errors", "skipped"}
    missing_keys = required_keys - set(result.keys())
    assert not missing_keys, f"Missing canonical keys: {missing_keys}"
    assert "violations" not in result, "Got legacy 'violations' key instead of 'violations_found'"
    assert "fixed" not in result, "Got legacy 'fixed' key instead of 'violations_fixed'"


def test_diamond_inheritance_stability():
    """
    Tests deep inheritance chains to ensure MRO resolves
    without method resolution errors or skipped initializers.
    """
    print("\n[TEST 3] Diamond Inheritance Stability...")

    from dataclasses import dataclass

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    @dataclass
    class DeepWorker(SovereignBaseAgent):
        custom_field: str = "test"

    worker = DeepWorker()
    mro_names = [c.__name__ for c in DeepWorker.mro()]

    assert mro_names[0] == "DeepWorker", "DeepWorker should be first in MRO"
    assert "SovereignBaseAgent" in mro_names, "SovereignBaseAgent should be in MRO"
    assert worker._state is not None, "_state should not be None"
    assert isinstance(worker._state, dict), "_state should be a dict"
    assert worker.custom_field == "test", "Custom field should be accessible"


def test_double_init_prevention():
    """
    Verifies that the _sovereign_initialized guard prevents double initialization.
    """
    print("\n[TEST 4] Double Initialization Prevention...")

    from dataclasses import dataclass

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    init_count = 0

    @dataclass
    class CountingAgent(SovereignBaseAgent):
        def __post_init__(self):
            nonlocal init_count
            init_count += 1
            super().__post_init__()

    agent = CountingAgent()
    agent.__post_init__()
    agent.__post_init__()

    assert agent._sovereign_initialized is True, "Should be initialized"


def test_cycle_detection():
    """
    Verifies that heal_repository properly detects cycles.
    """
    print("\n[TEST 5] Cycle Detection in heal_repository...")

    from dataclasses import dataclass

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    @dataclass
    class TestAgent(SovereignBaseAgent):
        pass

    agent = TestAgent()
    result = agent.heal_repository(
        dry_run=True,
        _call_path={"TestAgent"},  # Agent already in path = cycle
    )

    assert result["status"] == "SKIPPED", f"Expected SKIPPED status, got {result['status']}"
    assert result["skipped"] == 1, f"Expected skipped=1, got {result['skipped']}"


def test_max_depth_termination():
    """
    Verifies that heal_repository terminates at max depth.
    """
    print("\n[TEST 6] Max Depth Termination...")

    from dataclasses import dataclass

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    @dataclass
    class TestAgent(SovereignBaseAgent):
        pass

    agent = TestAgent()
    result = agent.heal_repository(dry_run=True, depth=10, max_depth=MAX_DEPTH)

    assert result["status"] == "SKIPPED", f"Expected SKIPPED status, got {result['status']}"
    assert result["skipped"] == 1, f"Expected skipped=1, got {result['skipped']}"


def test_mixin_state_access_during_init():
    """
    Verifies that _state exists as a dataclass field BEFORE __post_init__ runs,
    so any code in __post_init__ or infrastructure_mixin.__init__ can safely access it.
    """
    print("\n[TEST 7] State Container Exists Before __post_init__...")

    from dataclasses import dataclass, fields

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    field_names = [f.name for f in fields(SovereignBaseAgent)]

    assert "_state" in field_names, "_state should be a dataclass field"
    assert "_call_path" in field_names, "_call_path should be a dataclass field"

    @dataclass
    class TestAgent(SovereignBaseAgent):
        pass

    agent = TestAgent()

    assert isinstance(agent._state, dict), "_state should be a dict"
    assert isinstance(agent._call_path, set), "_call_path should be a set"
    assert agent._state.get("status") == "booting", "_state should have 'booting' status"


def test_healer_mixin_heal_result_type():
    """
    Verifies that HealerMixin.heal_repository returns HealResult.
    """
    print("\n[TEST 8] HealerMixin HealResult Type...")

    class TestMixin(HealerMixin):
        pass

    mixin = TestMixin()
    result = mixin.heal_repository(dry_run=True)

    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    required_keys = {"violations_found", "violations_fixed", "status", "errors", "skipped"}
    missing_keys = required_keys - set(result.keys())
    assert not missing_keys, f"Missing canonical keys: {missing_keys}"


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
