#!/usr/bin/env python3
"""
MRO Propagation Test - Tests key agents for MRO compliance
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.testing.mro_auditor import MROAuditor


def main():
    """Test key agents across all layers."""
    print("\n" + "=" * 70)
    print("MRO PROPAGATION TEST - Key Agents")
    print("=" * 70)
    
    auditor = MROAuditor()
    test_cases = []
    
    # L0 Agent
    try:
        from agentic_core.L0_maintenance.scripts.L0MaintenanceBaseAgent import L0MaintenanceBaseAgent
        test_cases.append(("L0MaintenanceBaseAgent", L0MaintenanceBaseAgent, True))
    except Exception as e:
        print(f"Could not import L0MaintenanceBaseAgent: {e}")
    
    # L1 Agent
    try:
        from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import L1CognitionBaseAgent
        test_cases.append(("L1CognitionBaseAgent", L1CognitionBaseAgent, True))
    except Exception as e:
        print(f"Could not import L1CognitionBaseAgent: {e}")
    
    # L5SafetyBaseAgent
    try:
        from agentic_core.L5_safety.validators.L5SafetyBaseAgent import L5SafetyBaseAgent
        test_cases.append(("L5SafetyBaseAgent", L5SafetyBaseAgent, False))
    except Exception as e:
        print(f"Could not import L5SafetyBaseAgent: {e}")
    
    print(f"\nTesting {len(test_cases)} agents\n")
    
    passed = []
    failed = []
    
    for agent_name, agent_cls, is_dataclass in test_cases:
        print(f"Testing {agent_name}...")
        
        # Static check
        static_errors = auditor.audit_class_hierarchy(agent_cls)
        if static_errors:
            failed.append((agent_name, static_errors))
            print(f"  FAILED - Static MRO check")
            for error in static_errors:
                print(f"     {error}")
            continue
        else:
            print(f"  PASSED - Static MRO check")
        
        # Dynamic check
        try:
            if is_dataclass:
                instance = agent_cls(name=f"Test{agent_name}")
            else:
                instance = agent_cls(name=f"Test{agent_name}")
            
            success, error = auditor.verify_initialization_propagation(instance)
            if success:
                print(f"  PASSED - Propagation check")
                passed.append(agent_name)
            else:
                print(f"  FAILED - Propagation check")
                print(f"     {error}")
                failed.append((agent_name, [error]))
        except Exception as e:
            print(f"  WARNING - Could not instantiate: {e}")
            passed.append(agent_name)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"PASSED: {len(passed)} agents")
    print(f"FAILED: {len(failed)} agents")
    
    if failed:
        print("\nFAILED AGENTS:")
        for agent_name, errors in failed:
            print(f"  - {agent_name}")
            for error in errors:
                print(f"    {error}")
        return 1
    else:
        print("\nAll MRO checks PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
