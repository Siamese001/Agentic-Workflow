#!/usr/bin/env python3
"""
Runtime Propagation Test for heal_repository **kwargs

Verifies that all L0-L5 base agents can accept unknown keyword arguments
in their heal_repository() methods without raising TypeError.

This ensures proper kwargs propagation through the MRO chain.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_l0_kwargs_propagation():
    """Test L0MaintenanceBaseAgent accepts unknown kwargs."""
    from agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent
    
    agent = L0MaintenanceBaseAgent()
    
    # Should NOT raise TypeError with unknown kwargs
    try:
        result = agent.heal_repository(dry_run=True, unknown_flag=123, custom_param="test")
        print("✅ L0MaintenanceBaseAgent: kwargs propagation successful")
        return True
    except TypeError as e:
        print(f"❌ L0MaintenanceBaseAgent: kwargs propagation FAILED - {e}")
        return False


def test_l3_kwargs_propagation():
    """Test L3OrchestrationBaseAgent accepts unknown kwargs."""
    from agentic_core.L3_orchestration.workflow_engines.L3OrchestrationBaseAgent import L3OrchestrationBaseAgent
    
    agent = L3OrchestrationBaseAgent()
    
    # Should NOT raise TypeError with unknown kwargs
    try:
        result = agent.heal_repository(dry_run=True, unknown_flag=456, extra_data={"test": True})
        print("✅ L3OrchestrationBaseAgent: kwargs propagation successful")
        return True
    except TypeError as e:
        print(f"❌ L3OrchestrationBaseAgent: kwargs propagation FAILED - {e}")
        return False


def test_l5_kwargs_propagation():
    """Test L5SafetyBaseAgent accepts unknown kwargs."""
    from agentic_core.L5_safety.validators.L5SafetyBaseAgent import L5SafetyBaseAgent
    
    agent = L5SafetyBaseAgent()
    
    # Should NOT raise TypeError with unknown kwargs
    try:
        result = agent.heal_repository(dry_run=True, mystery_param="value", debug_mode=True)
        print("✅ L5SafetyBaseAgent: kwargs propagation successful")
        return True
    except TypeError as e:
        print(f"❌ L5SafetyBaseAgent: kwargs propagation FAILED - {e}")
        return False


def test_l6_kwargs_propagation():
    """Test L6ObservabilityBaseAgent accepts unknown kwargs."""
    from agentic_core.L6_observability.L6ObservabilityBaseAgent import L6ObservabilityBaseAgent
    
    agent = L6ObservabilityBaseAgent()
    
    # Should NOT raise TypeError with unknown kwargs
    try:
        result = agent.heal_repository(dry_run=True, telemetry_flag=True, metrics_mode="detailed")
        print("✅ L6ObservabilityBaseAgent: kwargs propagation successful")
        return True
    except TypeError as e:
        print(f"❌ L6ObservabilityBaseAgent: kwargs propagation FAILED - {e}")
        return False


def main():
    """Run all kwargs propagation tests."""
    print("=" * 60)
    print("RUNTIME PROPAGATION TEST: heal_repository **kwargs")
    print("=" * 60)
    print()
    
    results = []
    
    # Test L0
    print("Testing L0 kwargs propagation...")
    results.append(test_l0_kwargs_propagation())
    print()
    
    # Test L3
    print("Testing L3 kwargs propagation...")
    results.append(test_l3_kwargs_propagation())
    print()
    
    # Test L5
    print("Testing L5 kwargs propagation...")
    results.append(test_l5_kwargs_propagation())
    print()
    
    # Test L6
    print("Testing L6 kwargs propagation...")
    results.append(test_l6_kwargs_propagation())
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print()
        print("SUCCESS: All base agents properly accept **kwargs in heal_repository()")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print()
        print("FAILURE: Some base agents do not accept **kwargs properly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
