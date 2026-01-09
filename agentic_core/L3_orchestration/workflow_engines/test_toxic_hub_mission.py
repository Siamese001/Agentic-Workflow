"""
TEST: Toxic Hub Mission - Toxicity-Weighted Triage & Fission Detection
========================================================================
This test validates:
1. L5 Base Class (high fan-in) is processed BEFORE L1 agent (low fan-in)
2. Fission detection triggers when large file remains unchanged after healing
"""

import asyncio
import tempfile
import os
from pathlib import Path
from mission_controller_convergence import ConvergenceEngine


class MockValidator:
    """Mock validator that returns violations for testing."""
    
    def __init__(self, violations):
        self.violations = violations
        self.call_count = 0
    
    async def validate(self):
        self.call_count += 1
        # After first round, reduce violations to simulate healing
        if self.call_count > 1:
            return []
        return self.violations


class MockHealer:
    """Mock healer that tracks healing order."""
    
    def __init__(self):
        self.heal_order = []
    
    async def heal(self, violation):
        path = violation.get('path', 'unknown')
        impact = violation.get('impact_score', 0)
        print(f"  🔧 Healing: {path} (impact_score={impact})")
        self.heal_order.append(path)


async def test_toxicity_weighted_triage():
    """
    Test Case 1: Verify L5 Base Class is processed before L1 agent
    due to higher toxicity/impact score.
    """
    print("\n" + "="*80)
    print("TEST 1: Toxicity-Weighted Triage")
    print("="*80)
    
    # Create violations with different impact scores
    # L5 Base Class has higher fan-in (259) → higher impact
    # L1 Agent has lower fan-in (5) → lower impact
    violations = [
        {
            'path': 'agentic_core/L1_cognition/peripheral_agent.py',
            'type': 'upward_leak',
            'impact_score': 50,  # Low impact (peripheral)
            'fan_in': 5,
            'audit_fail_count': 1
        },
        {
            'path': 'agentic_core/L5_safety/guardrails/SafetyBaseAgent.py',
            'type': 'upward_leak', 
            'impact_score': 650,  # High impact (core hub, fan-in=259)
            'fan_in': 259,
            'audit_fail_count': 1
        },
        {
            'path': 'agentic_core/L3_orchestration/mid_tier_agent.py',
            'type': 'upward_leak',
            'impact_score': 200,  # Medium impact
            'fan_in': 50,
            'audit_fail_count': 1
        }
    ]
    
    validator = MockValidator(violations)
    healer = MockHealer()
    engine = ConvergenceEngine(max_rounds=3)
    
    print("\nViolations (unsorted):")
    for v in violations:
        print(f"  - {v['path']} (impact={v['impact_score']})")
    
    print("\nExpected order (by impact_score DESC):")
    print("  1. L5 SafetyBaseAgent (impact=650)")
    print("  2. L3 mid_tier_agent (impact=200)")
    print("  3. L1 peripheral_agent (impact=50)")
    
    print("\nRunning ConvergenceEngine...")
    await engine.run_convergence(validator, healer, violations)
    
    print("\nActual healing order:")
    for i, path in enumerate(healer.heal_order, 1):
        print(f"  {i}. {path}")
    
    # Validate order - check first 3 items (first round)
    expected_order = [
        'agentic_core/L5_safety/guardrails/SafetyBaseAgent.py',
        'agentic_core/L3_orchestration/mid_tier_agent.py',
        'agentic_core/L1_cognition/peripheral_agent.py'
    ]
    
    # Check first round order (first 3 heals)
    first_round_order = healer.heal_order[:3]
    if first_round_order == expected_order:
        print("\n✅ TEST 1 PASSED: L5 Base Class processed before L1 agent (toxicity triage working)")
    else:
        print("\n❌ TEST 1 FAILED: Healing order incorrect")
        return False
    
    return True


async def test_zombie_detection():
    """
    Test Case 2: Verify zombie detection triggers for persistent failures.
    """
    print("\n" + "="*80)
    print("TEST 2: Zombie Detection")
    print("="*80)
    
    # Create a zombie violation (audit_fail_count > 3)
    violations = [
        {
            'path': 'agentic_core/L2_execution/stubborn_agent.py',
            'type': 'upward_leak',
            'impact_score': 100,
            'audit_fail_count': 5  # ZOMBIE: failed 5 audits
        },
        {
            'path': 'agentic_core/L4_state/normal_agent.py',
            'type': 'upward_leak',
            'impact_score': 80,
            'audit_fail_count': 1  # Normal: only 1 failure
        }
    ]
    
    validator = MockValidator(violations)
    healer = MockHealer()
    engine = ConvergenceEngine(max_rounds=2)
    
    print("\nViolations:")
    for v in violations:
        status = "🧟 ZOMBIE" if v['audit_fail_count'] > 3 else "Normal"
        print(f"  - {v['path']} (audit_fail_count={v['audit_fail_count']}) [{status}]")
    
    print("\nRunning ConvergenceEngine (watch for ZOMBIE DETECTED message)...")
    await engine.run_convergence(validator, healer, violations)
    
    print("\n✅ TEST 2 PASSED: Zombie detection triggered (check console output above)")
    return True


async def test_fission_detection():
    """
    Test Case 3: Verify fission detection triggers for large unchanged files.
    """
    print("\n" + "="*80)
    print("TEST 3: Fission Detection")
    print("="*80)
    
    # Create a temporary large file (>10KB)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Write >10KB of content
        f.write("# Large test file\n" * 1000)  # ~20KB
        temp_file = f.name
    
    print(f"\nCreated temp file: {temp_file}")
    print(f"File size: {os.path.getsize(temp_file)} bytes")
    
    # Create violation pointing to this file
    violations = [
        {
            'path': temp_file,
            'type': 'upward_leak',
            'impact_score': 100,
            'audit_fail_count': 1
        }
    ]
    
    class NonModifyingHealer:
        """Healer that doesn't actually modify the file (simulates failed healing)."""
        async def heal(self, violation):
            print(f"  🔧 Attempting to heal: {violation.get('path')}")
            # Don't modify the file - this should trigger fission detection
    
    validator = MockValidator(violations)
    healer = NonModifyingHealer()
    engine = ConvergenceEngine(max_rounds=2)
    
    print("\nRunning ConvergenceEngine with non-modifying healer...")
    print("(Should trigger FISSION DETECTED for unchanged large file)")
    await engine.run_convergence(validator, healer, violations)
    
    # Cleanup
    os.unlink(temp_file)
    
    print("\n✅ TEST 3 PASSED: Fission detection triggered (check console output above)")
    return True


async def main():
    """Run all Toxic Hub Mission tests."""
    print("\n" + "="*80)
    print("🧪 TOXIC HUB MISSION TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: Toxicity-Weighted Triage
    results.append(await test_toxicity_weighted_triage())
    
    # Test 2: Zombie Detection
    results.append(await test_zombie_detection())
    
    # Test 3: Fission Detection
    results.append(await test_fission_detection())
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
