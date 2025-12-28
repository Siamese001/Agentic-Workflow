#!/usr/bin/env python3
"""
Test script for L5 Safety Shield integration
"""
import asyncio
import json
from pathlib import Path

# Test imports
from agentic_core.L5_safety.guardrails.cached_safety_shield import CachedSafetyShield
from agentic_core.L5_safety.gravity.gravity_enforcer_agent import GravityEnforcerAgent
from agentic_core.L5_safety.policy.neural_auto_immune_agent import NeuralAutoImmuneAgent

class MockContext:
    """Mock context for testing"""
    def __init__(self):
        self.reports = []
    
    def report(self, agent, count, success, message):
        self.reports.append({
            'agent': agent,
            'count': count,
            'success': success,
            'message': message
        })
        print(f"   [REPORT] {agent}: {message}")

async def test_safety_shield():
    """Test the integrated safety shield system"""
    print("\n=== L5 Safety Shield Integration Test ===\n")
    
    project_root = Path("c:/Git/Agentic-Workflow")
    ctx = MockContext()
    
    # Test 1: CachedSafetyShield basic functionality
    print("[1] Testing CachedSafetyShield...")
    shield = CachedSafetyShield(project_root, "test_session")
    
    # Test cache storage and retrieval
    test_verdict = {"compliant": False, "territory": "test_domain", "reason": "Test violation"}
    shield.store_verdict("gravity", "test_file.py", test_verdict)
    
    cached = shield.get_cached_verdict("gravity", "test_file.py")
    if cached and cached.get("territory") == "test_domain":
        print("   ✓ CachedSafetyShield: Cache storage/retrieval working")
    else:
        print("   ✗ CachedSafetyShield: Cache test failed")
    
    # Test 2: GravityEnforcerAgent with cache
    print("\n[2] Testing GravityEnforcerAgent...")
    gravity_agent = GravityEnforcerAgent(project_root, ctx)
    
    # Test with a non-existent file (should handle gracefully)
    test_file = project_root / "test_gravity_check.py"
    result = gravity_agent._heal_file(test_file)
    print(f"   ✓ GravityEnforcerAgent: Handled file check (result: {result})")
    
    # Test 3: NeuralAutoImmuneAgent
    print("\n[3] Testing NeuralAutoImmuneAgent...")
    immune_agent = NeuralAutoImmuneAgent(project_root)
    
    # Store some test violations to trigger lockdown
    for i in range(6):  # Exceed threshold of 5
        test_verdict = {"compliant": False, "territory": "test_territory", "reason": f"Violation {i}"}
        shield.store_verdict("policy", f"test_item_{i}", test_verdict, ttl=3600)
    
    outbreaks = immune_agent.scan_for_outbreaks()
    if "test_territory" in outbreaks:
        print("   ✓ NeuralAutoImmuneAgent: Outbreak detection working")
    else:
        print("   ✗ NeuralAutoImmuneAgent: Outbreak detection failed")
    
    # Test 4: Integration test
    print("\n[4] Testing Integration...")
    
    # Simulate a workflow with cache hits
    print("   Simulating cached safety decisions...")
    
    # Store some cached verdicts
    shield.store_verdict("gravity", "file1.py", {"compliant": True, "had_violations": False})
    shield.store_verdict("policy", "prompt1", {"compliant": True, "safe": True})
    
    # Check cache hits
    cached_gravity = shield.get_cached_verdict("gravity", "file1.py")
    cached_policy = shield.get_cached_verdict("policy", "prompt1")
    
    if cached_gravity and cached_policy:
        print("   ✓ Integration: Multi-category cache working")
    else:
        print("   ✗ Integration: Cache issues detected")
    
    print("\n=== Test Complete ===")
    print(f"Total reports generated: {len(ctx.reports)}")
    for report in ctx.reports:
        print(f"  - {report['agent']}: {report['message']}")

if __name__ == "__main__":
    asyncio.run(test_safety_shield())
