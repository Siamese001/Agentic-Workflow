"""
MRO Refactor Verification Tests - Phase 21.1

Tests to verify that the MRO refactor was successful and all capabilities are retained.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc_mro_001_reporting_agent_initialization():
    """TC-MRO-001: ReportingAgent Initialization"""
    print("\n[TC-MRO-001] Testing ReportingAgent Initialization...")
    try:
        from agentic_core.L5_safety.validators.ReportingAgent import ReportingAgent

        agent = ReportingAgent(project_root=PROJECT_ROOT)

        # Check that config is populated (proves super().__init__() was called)
        assert hasattr(agent, "config"), "ReportingAgent missing 'config' attribute"
        print("   ✅ 100% PASS: ReportingAgent Initialized Base Attributes")
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_tc_mro_002_l4_state_base_agent_mro():
    """TC-MRO-002: L4StateBaseAgent MRO Check"""
    print("\n[TC-MRO-002] Testing L4StateBaseAgent MRO...")
    try:
        from agentic_core.L4_state.ValidationContext.L4StateBaseAgent import L4StateBaseAgent

        mro = L4StateBaseAgent.mro()
        mro_names = [cls.__name__ for cls in mro]

        print(f"   MRO: {' -> '.join(mro_names[:8])}...")

        # Verify L4SubatomicTestingMixin comes before SovereignBaseAgent
        l4_idx = (
            mro_names.index("L4SubatomicTestingMixin")
            if "L4SubatomicTestingMixin" in mro_names
            else -1
        )
        sovereign_idx = (
            mro_names.index("SovereignBaseAgent") if "SovereignBaseAgent" in mro_names else -1
        )
        infra_idx = (
            mro_names.index("InfrastructureMixin") if "InfrastructureMixin" in mro_names else -1
        )

        assert l4_idx >= 0, "L4SubatomicTestingMixin not in MRO"
        assert sovereign_idx >= 0, "SovereignBaseAgent not in MRO"
        assert infra_idx >= 0, "InfrastructureMixin not in MRO"
        assert l4_idx < sovereign_idx, (
            "L4SubatomicTestingMixin should come before SovereignBaseAgent"
        )
        assert sovereign_idx < infra_idx, (
            "SovereignBaseAgent should come before InfrastructureMixin"
        )

        print("   ✅ 100% PASS: MRO Linearity Verified")
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_tc_mro_003_semantic_debugger_inheritance():
    """TC-MRO-003: SemanticDebugger Inheritance"""
    print("\n[TC-MRO-003] Testing SemanticDebuggerAgent Inheritance...")
    try:
        from agentic_core.L5_safety.validators.SemanticDebuggerAgent import SemanticDebuggerAgent

        # If we get here without TypeError, the diamond problem is resolved
        agent = SemanticDebuggerAgent(project_root=PROJECT_ROOT)

        print("   ✅ 100% PASS: Diamond Problem Resolved")
        return True
    except TypeError as e:
        if "Cannot create a consistent method resolution order" in str(e):
            print(f"   ❌ FAIL: MRO conflict still exists - {e}")
        else:
            print(f"   ❌ FAIL: {e}")
        return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_tc_cap_001_redis_capability_retention():
    """TC-CAP-001: Redis Capability Retention"""
    print("\n[TC-CAP-001] Testing Redis Capability Retention...")
    try:
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent

        agent = AutonomyGuardianAgent(project_root=PROJECT_ROOT)

        # Check that cache_get exists (from RedisCacheMixin via InfrastructureMixin)
        has_cache_get = hasattr(agent, "cache_get")
        has_cache_set = hasattr(agent, "cache_set")

        assert has_cache_get, "AutonomyGuardianAgent missing 'cache_get' method"
        assert has_cache_set, "AutonomyGuardianAgent missing 'cache_set' method"

        print("   ✅ 100% PASS: Capabilities Retained")
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_tc_cap_002_healer_capability_retention():
    """TC-CAP-002: Healer Capability Retention"""
    print("\n[TC-CAP-002] Testing Healer Capability Retention...")
    try:
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent

        agent = DDDAlignmentAgent(project_root=PROJECT_ROOT)

        # Check that heal_repository exists (from HealerMixin via InfrastructureMixin)
        has_heal = hasattr(agent, "heal_repository")

        assert has_heal, "DDDAlignmentAgent missing 'heal_repository' method"

        print("   ✅ 100% PASS: Capabilities Retained")
        return True
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def run_all_tests():
    """Run all MRO refactor verification tests."""
    print("=" * 60)
    print("MRO REFACTOR VERIFICATION TESTS - Phase 21.1")
    print("=" * 60)

    results = []

    results.append(("TC-MRO-001", test_tc_mro_001_reporting_agent_initialization()))
    results.append(("TC-MRO-002", test_tc_mro_002_l4_state_base_agent_mro()))
    results.append(("TC-MRO-003", test_tc_mro_003_semantic_debugger_inheritance()))
    results.append(("TC-CAP-001", test_tc_cap_001_redis_capability_retention()))
    results.append(("TC-CAP-002", test_tc_cap_002_healer_capability_retention()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_id, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_id}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 100% PASS: MRO Refactor Verified Successfully!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
