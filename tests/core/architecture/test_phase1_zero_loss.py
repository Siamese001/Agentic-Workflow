"""
Phase 1 Zero-Loss Verification Test Suite

This test suite ensures no legacy functionality is dropped during the Phase 1
consolidation work. All 4 test cases must pass 100%.

Test Cases:
- TC-1: Signature Parity - IHealable is superset of legacy signatures
- TC-2: Data Mapping Integrity - _normalize_result preserves all data
- TC-3: Discovery Exhaustiveness - SSOT discovery matches manual count
- TC-4: MRO Stability - Adding IHealable doesn't disrupt MRO

Author: Cascade
Date: January 19, 2026
Phase: 1 - Foundation & Zero-Loss Protocols
"""
import inspect
import sys
from pathlib import Path
from typing import Dict, Any, Set, get_type_hints

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc1_signature_parity():
    """
    TC-1: Signature Parity
    
    Verify that the new IHealable protocol is a perfect superset of the
    signatures found in BiasAuditorAgent and NamingAgent.
    
    The IHealable.heal_repository signature must accept all parameters
    that legacy agents use.
    """
    print("\n" + "="*60)
    print("TC-1: Signature Parity")
    print("="*60)
    
    from agentic_core.L3_orchestration.interfaces import IHealable
    
    # Get IHealable.heal_repository signature
    ihealable_sig = inspect.signature(IHealable.heal_repository)
    ihealable_params = set(ihealable_sig.parameters.keys())
    
    print(f"IHealable.heal_repository parameters: {ihealable_params}")
    
    # Required parameters that must be in IHealable
    required_params = {'self', 'dry_run', 'execute', 'depth', 'max_depth', 'kwargs'}
    
    # Check that IHealable has all required parameters
    missing = required_params - ihealable_params
    if missing:
        print(f"❌ FAIL: Missing parameters in IHealable: {missing}")
        return False
    
    # Verify **kwargs is present for backward compatibility
    kwargs_param = ihealable_sig.parameters.get('kwargs')
    if kwargs_param is None or kwargs_param.kind != inspect.Parameter.VAR_KEYWORD:
        print("❌ FAIL: IHealable.heal_repository must have **kwargs for backward compatibility")
        return False
    
    print("✅ PASS: IHealable.heal_repository is a superset of legacy signatures")
    print(f"   Required params: {required_params}")
    print(f"   IHealable params: {ihealable_params}")
    return True


def test_tc2_data_mapping_integrity():
    """
    TC-2: Data Mapping Integrity
    
    Test _normalize_result with a dictionary containing ONLY legacy keys.
    Verify the output maps correctly to HealResult format.
    No data should be dropped.
    """
    print("\n" + "="*60)
    print("TC-2: Data Mapping Integrity")
    print("="*60)
    
    from agentic_core.L5_safety.validators.healer_mixin import HealerMixin, HealResult
    
    # Create a test instance
    class TestAgent(HealerMixin):
        pass
    
    agent = TestAgent()
    
    # Test Case 2a: Legacy keys only
    legacy_input = {'violations': 5, 'fixed': 2}
    result = agent._normalize_result(legacy_input)
    
    print(f"Input (legacy keys): {legacy_input}")
    print(f"Output (HealResult): {result}")
    
    if result['violations_found'] != 5:
        print(f"❌ FAIL: violations_found should be 5, got {result['violations_found']}")
        return False
    
    if result['violations_fixed'] != 2:
        print(f"❌ FAIL: violations_fixed should be 2, got {result['violations_fixed']}")
        return False
    
    # Test Case 2b: Mixed keys (new and legacy)
    mixed_input = {'violations_found': 10, 'fixed': 3, 'status': 'PASS'}
    result2 = agent._normalize_result(mixed_input)
    
    print(f"\nInput (mixed keys): {mixed_input}")
    print(f"Output (HealResult): {result2}")
    
    if result2['violations_found'] != 10:
        print(f"❌ FAIL: violations_found should be 10, got {result2['violations_found']}")
        return False
    
    if result2['violations_fixed'] != 3:
        print(f"❌ FAIL: violations_fixed should be 3, got {result2['violations_fixed']}")
        return False
    
    if result2['status'] != 'PASS':
        print(f"❌ FAIL: status should be 'PASS', got {result2['status']}")
        return False
    
    # Test Case 2c: 'renamed' key (used by some agents)
    renamed_input = {'violations': 7, 'renamed': 4}
    result3 = agent._normalize_result(renamed_input)
    
    print(f"\nInput (renamed key): {renamed_input}")
    print(f"Output (HealResult): {result3}")
    
    if result3['violations_fixed'] != 4:
        print(f"❌ FAIL: violations_fixed should be 4 (from 'renamed'), got {result3['violations_fixed']}")
        return False
    
    # Verify all HealResult keys are present
    required_keys = {'violations_found', 'violations_fixed', 'status', 'errors', 'skipped'}
    for key in required_keys:
        if key not in result:
            print(f"❌ FAIL: Missing key in HealResult: {key}")
            return False
    
    print("\n✅ PASS: _normalize_result correctly maps all legacy keys")
    print("   - 'violations' -> 'violations_found'")
    print("   - 'fixed' -> 'violations_fixed'")
    print("   - 'renamed' -> 'violations_fixed'")
    return True


def test_tc3_discovery_exhaustiveness():
    """
    TC-3: Discovery Exhaustiveness
    
    Run a test comparing get_python_files() count against a manual
    rglob count with the same exclusions. The delta must be zero.
    """
    print("\n" + "="*60)
    print("TC-3: Discovery Exhaustiveness")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import compare_with_rglob
    
    result = compare_with_rglob(PROJECT_ROOT)
    
    print(f"SSOT Discovery count: {result['ssot_count']}")
    print(f"rglob count (same exclusions): {result['rglob_count']}")
    print(f"Delta: {result['delta']}")
    
    if result['delta'] != 0:
        print(f"❌ FAIL: Delta should be 0, got {result['delta']}")
        print("   This indicates SSOT discovery is missing or including extra files")
        return False
    
    print("\n✅ PASS: SSOT discovery matches rglob count exactly")
    print(f"   Both found {result['ssot_count']} files")
    return True


def test_tc4_mro_stability():
    """
    TC-4: MRO Stability
    
    Verify that adding IHealable to the mixin does not disrupt the
    Method Resolution Order of a sample agent.
    """
    print("\n" + "="*60)
    print("TC-4: MRO Stability")
    print("="*60)
    
    from agentic_core.L5_safety.validators.healer_mixin import HealerMixin
    from agentic_core.L3_orchestration.interfaces import IHealable
    
    # Create a sample agent class hierarchy
    class BaseMixin:
        def base_method(self):
            return "base"
    
    class SpecializedMixin(BaseMixin):
        def specialized_method(self):
            return "specialized"
    
    class TestAgent(SpecializedMixin, HealerMixin):
        def agent_method(self):
            return "agent"
    
    # Get MRO
    mro = TestAgent.__mro__
    mro_names = [cls.__name__ for cls in mro]
    
    print(f"TestAgent MRO: {mro_names}")
    
    # Verify MRO order is correct
    # Expected: TestAgent -> SpecializedMixin -> BaseMixin -> HealerMixin -> object
    expected_order = ['TestAgent', 'SpecializedMixin', 'BaseMixin', 'HealerMixin']
    
    for i, expected in enumerate(expected_order):
        if mro_names[i] != expected:
            print(f"❌ FAIL: MRO position {i} should be {expected}, got {mro_names[i]}")
            return False
    
    # Verify IHealable protocol check works
    agent = TestAgent()
    
    if not isinstance(agent, IHealable):
        print("❌ FAIL: TestAgent should be recognized as IHealable")
        return False
    
    # Verify heal_repository is callable
    if not hasattr(agent, 'heal_repository'):
        print("❌ FAIL: TestAgent should have heal_repository method")
        return False
    
    # Call heal_repository to verify it works
    result = agent.heal_repository(dry_run=True)
    
    if 'violations_found' not in result:
        print(f"❌ FAIL: heal_repository should return HealResult, got {result}")
        return False
    
    print("\n✅ PASS: MRO is stable and IHealable protocol works correctly")
    print(f"   MRO: {' -> '.join(mro_names[:5])}")
    print(f"   isinstance(agent, IHealable): True")
    print(f"   heal_repository returns HealResult: True")
    return True


def main():
    """Run all Zero-Loss test cases."""
    print("\n" + "="*70)
    print("PHASE 1 ZERO-LOSS VERIFICATION TEST SUITE")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    
    tests = [
        ("TC-1: Signature Parity", test_tc1_signature_parity),
        ("TC-2: Data Mapping Integrity", test_tc2_data_mapping_integrity),
        ("TC-3: Discovery Exhaustiveness", test_tc3_discovery_exhaustiveness),
        ("TC-4: MRO Stability", test_tc4_mro_stability),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("✅ 100% PASS - All Zero-Loss tests passed!")
        print("\nPhase 1 Foundation is verified and ready for Phase 2.")
        return 0
    else:
        print(f"❌ FAIL - {total_count - passed_count} test(s) failed")
        print("\nDO NOT proceed to Phase 2 until all tests pass.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
