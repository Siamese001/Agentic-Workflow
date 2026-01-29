#!/usr/bin/env python3
"""
Test script to reproduce the heal_violation issue with LocationAgent.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

def test_location_agent_heal_method():
    """Test if LocationAgent has the required heal method."""
    
    print("Testing LocationAgent heal method...")
    
    # Initialize LocationAgent
    agent = LocationAgent(project_root)
    
    # Check if heal method exists
    if hasattr(agent, 'heal'):
        print("✓ LocationAgent has heal method")
        
        # Try to call it with a mock violation
        mock_violation = {
            'type': 'LOCATION',
            'file': str(project_root / 'test_file.py'),
            'message': 'Test violation'
        }
        
        try:
            result = agent.heal(mock_violation)
            print(f"✓ heal method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"✗ heal method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal method")
        print(f"  Available methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        return False
    
    return True

def test_heal_violations_method():
    """Test if LocationAgent has heal_violations method."""
    
    print("\nTesting LocationAgent heal_violations method...")
    
    agent = LocationAgent(project_root)
    
    if hasattr(agent, 'heal_violations'):
        print("✓ LocationAgent has heal_violations method")
        
        # Try to call it
        violations = [
            (Path('test_file.py'), 'Test violation')
        ]
        
        try:
            result = agent.heal_violations(violations)
            print(f"✓ heal_violations method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"✗ heal_violations method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal_violations method")
        return False
    
    return True

if __name__ == "__main__":
    print("=== LocationAgent Healing Method Test ===\n")
    
    heal_test = test_location_agent_heal_method()
    heal_violations_test = test_heal_violations_method()
    
    print("\n=== Test Results ===")
    print(f"heal method: {'PASS' if heal_test else 'FAIL'}")
    print(f"heal_violations method: {'PASS' if heal_violations_test else 'FAIL'}")
    
    if not heal_test or not heal_violations_test:
        print("\n⚠️  LocationAgent needs to implement proper healing methods for execute_ssot.py")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
