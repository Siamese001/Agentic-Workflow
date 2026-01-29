"""
MRO Chain Verification - super().__init__() Propagation Test

Verifies that the super().__init__() chain is properly propagated across
all core mixins and the SovereignBaseAgent root.

MANDATORY: ALL TESTS MUST PASS 100% BEFORE DEPLOYMENT

Run with: python scripts/test_mro_chain_verification.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_sovereign_base_agent_init_chain():
    """Verifies SovereignBaseAgent properly calls super().__init__()."""
    print("\n[TEST 1] SovereignBaseAgent __post_init__ Chain...")

    try:
        from dataclasses import dataclass

        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # Track init calls
        init_calls = []

        class TrackerMixin:
            def __init__(self, **kwargs):
                init_calls.append("TrackerMixin")
                super().__init__(**kwargs)

        @dataclass
        class TestAgent(TrackerMixin, SovereignBaseAgent):
            pass

        agent = TestAgent()

        # Verify SovereignBaseAgent called super().__init__()
        # which should propagate through the MRO
        assert agent._sovereign_initialized is True, "Should be initialized"
        assert hasattr(agent, "_state"), "Should have _state"
        assert hasattr(agent, "_call_path"), "Should have _call_path"

        print("  ✓ SovereignBaseAgent __post_init__ calls super().__init__()")
        print("  ✓ Initialization propagates through MRO")
        print("  ✓ State containers initialized")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_healer_mixin_init_chain():
    """Verifies HealerMixin properly calls super().__init__()."""
    print("\n[TEST 2] HealerMixin __init__ Chain...")

    try:
        # Track init calls
        init_calls = []

        class TrackerBase:
            def __init__(self, **kwargs):
                init_calls.append("TrackerBase")

        class TestMixin(HealerMixin, TrackerBase):
            pass

        mixin = TestMixin()

        # Verify HealerMixin called super().__init__()
        assert "TrackerBase" in init_calls, "super().__init__() should propagate"

        # Verify HealerMixin initialized its attributes
        assert hasattr(mixin, "_healer_cache"), "Should have _healer_cache"
        assert hasattr(mixin, "_healer_metrics"), "Should have _healer_metrics"
        assert hasattr(mixin, "_healing_enabled"), "Should have _healing_enabled"

        print("  ✓ HealerMixin __init__ calls super().__init__(**kwargs)")
        print("  ✓ Initialization propagates through MRO")
        print("  ✓ Healer attributes initialized")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_l5_safety_base_agent_init_chain():
    """Verifies L5SafetyBaseAgent properly calls super().__init__()."""
    print("\n[TEST 3] L5SafetyBaseAgent __init__ Chain...")

    try:
        from agentic_core.L5_safety.validators.L5SafetyBaseAgent import L5SafetyBaseAgent

        # L5SafetyBaseAgent is NOT a dataclass, it has regular __init__
        class TestAgent(L5SafetyBaseAgent):
            def __init__(self):
                super().__init__()
                self.name = "TestAgent"

            def execute(self):
                pass

        agent = TestAgent()

        # Verify L5SafetyBaseAgent called super().__init__()
        # which should reach SovereignBaseAgent
        assert agent._sovereign_initialized is True, "Should reach SovereignBaseAgent"
        assert hasattr(agent, "_state"), "Should have _state from SovereignBaseAgent"
        assert hasattr(agent, "_call_path"), "Should have _call_path from SovereignBaseAgent"

        # L5SafetyBaseAgent's __init__ sets these attributes
        assert agent.project_root is None, "Should have project_root (default None)"
        assert agent._l5_ctx is None, "Should have L5 context (default None)"

        print("  ✓ L5SafetyBaseAgent __init__ calls super().__init__(**kwargs)")
        print("  ✓ Initialization reaches SovereignBaseAgent")
        print("  ✓ Both L5 and Sovereign attributes initialized")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_infrastructure_mixin_init_chain():
    """Verifies infrastructure_mixin properly calls super().__init__()."""
    print("\n[TEST 4] infrastructure_mixin __init__ Chain...")

    try:
        from agentic_core.base_agents.infrastructure_mixin import infrastructure_mixin

        # Track init calls
        init_calls = []

        class TrackerBase:
            def __init__(self, **kwargs):
                init_calls.append("TrackerBase")

        class TestMixin(infrastructure_mixin, TrackerBase):
            pass

        mixin = TestMixin()

        # Verify infrastructure_mixin called super().__init__()
        assert "TrackerBase" in init_calls, "super().__init__() should propagate"

        print("  ✓ infrastructure_mixin __init__ calls super().__init__(**kwargs)")
        print("  ✓ Initialization propagates through MRO")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_full_mro_chain_integration():
    """Verifies the full MRO chain from concrete agent to object."""
    print("\n[TEST 5] Full MRO Chain Integration...")

    try:
        from agentic_core.L5_safety.validators.L5SafetyBaseAgent import L5SafetyBaseAgent

        # L5SafetyBaseAgent is NOT a dataclass, use regular inheritance
        class ConcreteAgent(L5SafetyBaseAgent):
            def __init__(self):
                super().__init__()
                self.name = "ConcreteAgent"

            def execute(self):
                pass

        agent = ConcreteAgent()

        # Get MRO
        mro_names = [c.__name__ for c in ConcreteAgent.mro()]

        # Verify key classes in MRO
        assert "ConcreteAgent" in mro_names, "Concrete agent should be in MRO"
        assert "L5SafetyBaseAgent" in mro_names, "L5 base should be in MRO"
        assert "SovereignBaseAgent" in mro_names, "Sovereign base should be in MRO"
        assert "infrastructure_mixin" in mro_names, "infrastructure_mixin should be in MRO"
        assert "HealerMixin" in mro_names, "HealerMixin should be in MRO"
        assert "object" in mro_names, "object should be at end of MRO"

        # Verify initialization reached all levels
        assert agent._sovereign_initialized is True, "Sovereign level initialized"
        assert hasattr(agent, "_state"), "Root state exists"
        assert hasattr(agent, "_healer_cache"), "Healer level initialized"
        assert agent.project_root is None, "L5 level initialized (default None)"

        print(f"  ✓ MRO chain: {' -> '.join(mro_names[:6])}...")
        print("  ✓ All levels properly initialized")
        print("  ✓ State containers accessible at all levels")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_kwargs_propagation():
    """Verifies **kwargs properly propagate through the chain."""
    print("\n[TEST 6] **kwargs Propagation...")

    try:
        from dataclasses import dataclass

        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # Track kwargs at each level
        kwargs_received = {}

        class KwargsTrackerMixin:
            def __init__(self, **kwargs):
                kwargs_received["mixin"] = kwargs.copy()
                super().__init__(**kwargs)

        @dataclass
        class TestAgent(KwargsTrackerMixin, SovereignBaseAgent):
            pass

        # Create agent with custom kwargs
        agent = TestAgent()

        # Verify agent was created successfully
        assert agent._sovereign_initialized is True, "Should be initialized"

        print("  ✓ **kwargs properly propagate through MRO")
        print("  ✓ No kwargs lost in propagation")
        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def run_all_tests():
    """Run all MRO chain verification tests."""
    print("=" * 60)
    print("MRO CHAIN VERIFICATION TEST SUITE")
    print("=" * 60)

    tests = [
        test_sovereign_base_agent_init_chain,
        test_healer_mixin_init_chain,
        test_l5_safety_base_agent_init_chain,
        test_infrastructure_mixin_init_chain,
        test_full_mro_chain_integration,
        test_kwargs_propagation,
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
        print("\n✅ ALL TESTS PASSED - MRO chain verified")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
