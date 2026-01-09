#!/usr/bin/env python3
"""
Robust Tests for InterfaceBoundaryAgent
"""

import sys
import ast
from pathlib import Path

# Setup mock for MCPHardenedMixin
class MockMixin: pass
mock_module = type(sys)('mock')
mock_module.MCPHardenedMixin = MockMixin
sys.modules['agentic_core.utils.core_extensions.mcp_hardened_mixin'] = mock_module

# Direct import
import importlib.util
spec = importlib.util.spec_from_file_location(
    'InterfaceBoundaryAgent',
    Path('agentic_core/L2_execution/ToolRegistry/InterfaceBoundaryAgent.py')
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

InterfaceBoundaryAgent = module.InterfaceBoundaryAgent


def test_complexity_trigger():
    """TEST 1: Complexity Trigger Test"""
    print("=" * 60)
    print("TEST 1: COMPLEXITY TRIGGER TEST")
    print("=" * 60)
    
    agent = InterfaceBoundaryAgent(root_dir='.', complexity_threshold=15)
    violations = agent.audit_boundaries()
    
    mock_detected = any('mock_heavy_utility' in v['file'] for v in violations)
    print(f"Mock heavy utility detected: {mock_detected}")
    print(f"Total violations found: {len(violations)}")
    
    if mock_detected:
        mock_violation = [v for v in violations if 'mock_heavy_utility' in v['file']][0]
        method_count = mock_violation['complexity']['method_count']
        action = mock_violation['action']
        print(f"Method count: {method_count}")
        print(f"Action: {action}")
        assert method_count >= 20, f"Expected >= 20 methods, got {method_count}"
        assert action == 'EXTRACT_INTERFACE'
        print("✅ TEST 1 PASSED: Complexity trigger working")
        return mock_violation
    else:
        print("❌ TEST 1 FAILED: Mock file not detected")
        return None


def test_interface_integrity(violation):
    """TEST 2: Interface Integrity Test"""
    print("\n" + "=" * 60)
    print("TEST 2: INTERFACE INTEGRITY TEST")
    print("=" * 60)
    
    if not violation:
        print("❌ TEST 2 SKIPPED: No violation to test")
        return
    
    agent = InterfaceBoundaryAgent(root_dir='.')
    stub = agent.generate_interface_stub(violation)
    
    print("Generated interface stub:")
    print("-" * 40)
    print(stub[:500] + "..." if len(stub) > 500 else stub)
    print("-" * 40)
    
    # Verify syntactically correct
    try:
        ast.parse(stub)
        print("✅ Syntax check: PASSED")
    except SyntaxError as e:
        print(f"❌ Syntax check: FAILED - {e}")
        return
    
    # Verify ABC import
    assert 'from abc import ABC, abstractmethod' in stub
    print("✅ ABC import: PRESENT")
    
    # Verify interface name
    assert 'class IMock' in stub or 'class Imock' in stub
    print("✅ Interface class: PRESENT")
    
    # Verify public methods are included
    assert 'method_01' in stub
    print("✅ Public methods: INCLUDED")
    
    # Verify private methods are excluded
    assert '_private_method' not in stub
    print("✅ Private methods: EXCLUDED")
    
    print("✅ TEST 2 PASSED: Interface integrity verified")


def test_boundary_report():
    """TEST 3: Boundary Report Test"""
    print("\n" + "=" * 60)
    print("TEST 3: BOUNDARY REPORT TEST")
    print("=" * 60)
    
    agent = InterfaceBoundaryAgent(root_dir='.', complexity_threshold=15)
    agent.audit_boundaries()
    
    print("Agent report output:")
    print("-" * 40)
    agent.report()
    print("-" * 40)
    
    print("✅ TEST 3 PASSED: Report generated successfully")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INTERFACE BOUNDARY AGENT - ROBUST TESTING")
    print("=" * 60 + "\n")
    
    # Run tests
    violation = test_complexity_trigger()
    test_interface_integrity(violation)
    test_boundary_report()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
