#!/usr/bin/env python3
"""Test the BaseClassEnforcerAgent."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.BaseClassEnforcerAgent import get_base_class_enforcer

def main():
    enforcer = get_base_class_enforcer(project_root)
    result = enforcer.scan_violations()
    
    print("=== Base Class Enforcement Report ===")
    print(f"Total Layer Agents: {result.get('total_layer_agents', 0)}")
    print(f"Compliant: {result.get('compliant_count', 0)}")
    print(f"Violations: {result.get('violation_count', 0)}")
    print(f"Compliance Rate: {result.get('compliance_rate', 0)}%")
    
    if result.get('violations'):
        print(f"\nSample Violations (first 10):")
        for v in result['violations'][:10]:
            print(f"  {v['class_name']} ({v['layer']}): expected {v['expected_base']}")
            print(f"    current: {v['current_bases']}")

if __name__ == "__main__":
    main()
