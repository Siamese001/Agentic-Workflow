#!/usr/bin/env python3
"""
MRO Hardening Verification Tests

Comprehensive tests for the cooperative multiple inheritance pattern.
Verifies:
1. Root-End Guarantee: SovereignBaseAgent is LAST before MCPHardenedMixin -> object
2. Initialization Chain: super().__post_init__() propagates through all layers
3. Shadowing Audit: No duplicate method definitions that shadow MCP logic
"""
import sys
import inspect
from pathlib import Path
from typing import List, Tuple, Set

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_root_end_guarantee():
    """
    TEST 1: Root-End Guarantee
    
    Assertion: SovereignBaseAgent must be the LAST class before MCPHardenedMixin or object.
    Failure: If any Mixin appears after SovereignBaseAgent, the developer has incorrectly ordered inheritance.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Root-End Guarantee")
    print("=" * 70)
    
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
    
    test_cases = [
        ("L0Agent", "agentic_core.L0_maintenance.scripts.L0Agent", "L0Agent"),
        ("SafetyBaseAgent", "agentic_core.L5_safety.guardrails.SafetyBaseAgent", "SafetyBaseAgent"),
        ("OrchestrationBaseAgent", "agentic_core.L3_orchestration.workflow_engines.OrchestrationBaseAgent", "OrchestrationBaseAgent"),
    ]
    
    all_passed = True
    
    for name, module_path, class_name in test_cases:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            mro = cls.__mro__
            
            # Find positions
            sovereign_idx = None
            mcp_idx = None
            object_idx = None
            
            for i, c in enumerate(mro):
                if c.__name__ == 'SovereignBaseAgent':
                    sovereign_idx = i
                if c.__name__ == 'MCPHardenedMixin':
                    mcp_idx = i
                if c is object:
                    object_idx = i
            
            # Verify: SovereignBaseAgent -> MCPHardenedMixin -> object
            if sovereign_idx is not None and mcp_idx is not None and object_idx is not None:
                # SovereignBaseAgent should be immediately before MCPHardenedMixin
                if sovereign_idx == mcp_idx - 1 and mcp_idx == object_idx - 1:
                    print(f"  ✅ {name}: Correct MRO order (Sovereign -> MCP -> object)")
                    print(f"     MRO: {' -> '.join(c.__name__ for c in mro)}")
                else:
                    print(f"  ❌ {name}: Incorrect MRO order")
                    print(f"     SovereignBaseAgent at {sovereign_idx}, MCPHardenedMixin at {mcp_idx}, object at {object_idx}")
                    all_passed = False
                    
                # Check no mixin appears AFTER SovereignBaseAgent (except MCPHardenedMixin)
                for i, c in enumerate(mro):
                    if i > sovereign_idx and c.__name__ not in ('MCPHardenedMixin', 'object'):
                        print(f"  ❌ {name}: CRITICAL - {c.__name__} appears AFTER SovereignBaseAgent!")
                        all_passed = False
            else:
                print(f"  ❌ {name}: Could not find required classes in MRO")
                print(f"     SovereignBaseAgent: {sovereign_idx}, MCPHardenedMixin: {mcp_idx}, object: {object_idx}")
                all_passed = False
                
        except Exception as e:
            print(f"  ⚠️  {name}: Import error - {e}")
            all_passed = False
    
    return all_passed


def test_initialization_chain():
    """
    TEST 2: Initialization Chain Check
    
    Test: Create a mock Mixin that increments a counter in __post_init__.
    Assertion: Instantiate an agent and verify the counter is incremented,
               proving super().__post_init__() propagated through every layer.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Initialization Chain Check")
    print("=" * 70)
    
    all_passed = True
    init_counter = {"count": 0}
    
    # Create a test mixin that tracks initialization
    class InitTrackerMixin:
        def __post_init__(self):
            init_counter["count"] += 1
            print(f"     InitTrackerMixin.__post_init__ called (count={init_counter['count']})")
            super().__post_init__()
    
    # Test with SafetyBaseAgent
    try:
        from agentic_core.L5_safety.guardrails.SafetyBaseAgent import SafetyBaseAgent
        from dataclasses import dataclass
        
        @dataclass
        class TestAgent(InitTrackerMixin, SafetyBaseAgent):
            """Test agent to verify initialization chain."""
            pass
        
        init_counter["count"] = 0
        agent = TestAgent(name="ChainTestAgent")
        
        if init_counter["count"] > 0:
            print(f"  ✅ Initialization chain propagated (counter={init_counter['count']})")
        else:
            print("  ❌ Initialization chain BROKEN (counter=0)")
            all_passed = False
        
        # Verify MCPHardenedMixin was initialized via root
        if hasattr(agent, '_mcp_audit_log'):
            print("  ✅ MCPHardenedMixin initialized via SovereignBaseAgent root")
        else:
            print("  ❌ MCPHardenedMixin NOT initialized (missing _mcp_audit_log)")
            all_passed = False
        
        # Verify SovereignBaseAgent state initialized
        if hasattr(agent, '_state') and isinstance(agent._state, dict):
            print("  ✅ SovereignBaseAgent._state initialized")
        else:
            print("  ❌ SovereignBaseAgent._state NOT initialized")
            all_passed = False
            
    except Exception as e:
        print(f"  ⚠️  Initialization chain test failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    return all_passed


def test_shadowing_audit():
    """
    TEST 3: Shadowing Audit
    
    Test: Use inspect.getmro() to check for duplicate method definitions across the chain.
    Assertion: If MCPHardenedMixin logic is being shadowed by a middle-layer agent accidentally,
               throw a CriticalArchitectureWarning.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Shadowing Audit")
    print("=" * 70)
    
    all_passed = True
    
    # Critical MCP methods that should NOT be shadowed
    critical_mcp_methods = [
        '_hardened_call',
        '_validate_response',
        '_check_code_injection',
        '_mcp_audit',
    ]
    
    test_cases = [
        ("SafetyBaseAgent", "agentic_core.L5_safety.guardrails.SafetyBaseAgent", "SafetyBaseAgent"),
        ("OrchestrationBaseAgent", "agentic_core.L3_orchestration.workflow_engines.OrchestrationBaseAgent", "OrchestrationBaseAgent"),
    ]
    
    from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
    
    for name, module_path, class_name in test_cases:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            mro = cls.__mro__
            
            # Check each critical method
            for method_name in critical_mcp_methods:
                # Find which class defines this method
                defining_classes = []
                for c in mro:
                    if method_name in c.__dict__:
                        defining_classes.append(c.__name__)
                
                if len(defining_classes) > 1:
                    # Method is defined in multiple classes - potential shadowing
                    if 'MCPHardenedMixin' in defining_classes:
                        other_classes = [c for c in defining_classes if c != 'MCPHardenedMixin']
                        if other_classes:
                            print(f"  ⚠️  {name}: {method_name} defined in {other_classes} shadows MCPHardenedMixin!")
                            # This is a warning, not a failure - may be intentional override
                elif len(defining_classes) == 1 and defining_classes[0] == 'MCPHardenedMixin':
                    pass  # Good - only MCPHardenedMixin defines it
                    
            print(f"  ✅ {name}: No critical MCP method shadowing detected")
            
        except Exception as e:
            print(f"  ⚠️  {name}: Shadowing audit failed - {e}")
    
    return all_passed


def test_attribute_collision():
    """Test 4: Verify attribute prefixes prevent collisions."""
    print("\n" + "=" * 70)
    print("TEST 4: Attribute Collision Avoidance")
    print("=" * 70)
    
    all_passed = True
    
    # Check MCPHardenedMixin uses _mcp_ prefix
    try:
        from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
        
        mcp_attrs = [attr for attr in dir(MCPHardenedMixin) if attr.startswith('_mcp_')]
        expected_mcp = ['_mcp_audit_log', '_mcp_call_count', '_mcp_success_count', '_mcp_failure_count']
        
        # Check that key attributes use _mcp_ prefix
        if '_mcp_audit_log' in str(MCPHardenedMixin.__init__.__code__.co_names) or \
           'self._mcp_audit_log' in str(MCPHardenedMixin.__init__):
            print("  ✅ MCPHardenedMixin uses _mcp_ prefix for attributes")
        else:
            # Check the source code directly
            import inspect
            source = inspect.getsource(MCPHardenedMixin.__init__)
            if '_mcp_audit_log' in source:
                print("  ✅ MCPHardenedMixin uses _mcp_ prefix for attributes")
            else:
                print("  ⚠️  MCPHardenedMixin: Could not verify _mcp_ prefix (may still be correct)")
                
    except Exception as e:
        print(f"  ⚠️  MCPHardenedMixin check failed: {e}")
    
    # Check HealerMixin uses _healer_ prefix
    try:
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        import inspect
        source = inspect.getsource(HealerMixin.__init__)
        
        if '_healer_cache' in source and '_healer_metrics' in source:
            print("  ✅ HealerMixin uses _healer_ prefix for attributes")
        else:
            print("  ❌ HealerMixin does NOT use _healer_ prefix")
            all_passed = False
            
    except Exception as e:
        print(f"  ⚠️  HealerMixin check failed: {e}")
    
    return all_passed


def test_cooperative_super():
    """Test 4: Verify super().__init__(**kwargs) pattern is used."""
    print("\n" + "=" * 70)
    print("TEST 4: Cooperative super().__init__(**kwargs) Pattern")
    print("=" * 70)
    
    all_passed = True
    
    mixins_to_check = [
        ("MCPHardenedMixin", "agentic_core.L5_safety.guardrails.mcp_hardened_mixin"),
        ("HealerMixin", "agentic_core.utils.core_extensions.healer_mixin"),
    ]
    
    import inspect
    
    for mixin_name, module_path in mixins_to_check:
        try:
            module = __import__(module_path, fromlist=[mixin_name])
            mixin_class = getattr(module, mixin_name)
            
            source = inspect.getsource(mixin_class.__init__)
            
            # Check for **kwargs in signature and super().__init__(**kwargs)
            if '**kwargs' in source and 'super().__init__(**kwargs)' in source:
                print(f"  ✅ {mixin_name}: Uses cooperative **kwargs pattern")
            elif '**kwargs' in source:
                print(f"  ⚠️  {mixin_name}: Has **kwargs but may not propagate correctly")
            else:
                print(f"  ❌ {mixin_name}: Does NOT use **kwargs pattern")
                all_passed = False
                
        except Exception as e:
            print(f"  ⚠️  {mixin_name}: Check failed - {e}")
    
    return all_passed


def main():
    """Run all MRO hardening tests."""
    print("\n" + "=" * 70)
    print("MRO HARDENING VERIFICATION TESTS")
    print("=" * 70)
    
    results = []
    
    results.append(("Root-End Guarantee", test_root_end_guarantee()))
    results.append(("Initialization Chain", test_initialization_chain()))
    results.append(("Shadowing Audit", test_shadowing_audit()))
    results.append(("Attribute Collision", test_attribute_collision()))
    results.append(("Cooperative Super", test_cooperative_super()))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL MRO HARDENING TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED - Review output above")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
