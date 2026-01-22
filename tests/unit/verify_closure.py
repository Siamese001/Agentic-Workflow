#!/usr/bin/env python3
"""
Verify Closure - Phase 16 Final Architectural Closure Tests.

Tests:
1. Zombie Healer detection
2. Init Bypass detection
3. Full Sentinel scan validation

Usage:
    python tests/verify_closure.py
"""

from __future__ import annotations
import sys
import os
import ast
from pathlib import Path

# Add root to path
sys.path.insert(0, os.getcwd())

from agentic_core.L5_safety.validators.CanonDependencySentinelAgent import (
    CanonDependencySentinelAgent, 
    InitializationIntegrityVisitor,
    HealerComplianceVisitor,
    ArchitectureDNAVisitor,
)


def test_zombie_healer():
    """Test ZOMBIE_HEALER detection."""
    print("\n[TEST 1] Zombie Healer Detection...")
    
    zombie_code = """
class ZombieAgent(SovereignBaseAgent):
    def heal_repository(self):
        pass
"""
    tree = ast.parse(zombie_code)
    visitor = HealerComplianceVisitor("zombie.py")
    visitor.visit(tree)
    
    if any(v.violation_type == "ZOMBIE_HEALER" for v in visitor.violations):
        print("✅ PASS: Zombie Healer detected.")
        return True
    else:
        print("❌ FAIL: Zombie Healer NOT detected.")
        return False


def test_init_bypass():
    """Test INIT_BYPASS detection."""
    print("\n[TEST 2] Init Bypass Detection...")
    
    bypass_code = """
class BadInitAgent(SovereignBaseAgent):
    def __init__(self):
        self.x = 1
"""
    tree = ast.parse(bypass_code)
    visitor = InitializationIntegrityVisitor("bad_init.py")
    visitor.visit(tree)
    
    if any(v.violation_type == "INIT_BYPASS" for v in visitor.violations):
        print("✅ PASS: Init Bypass detected.")
        return True
    else:
        print("❌ FAIL: Init Bypass NOT detected.")
        return False


def test_dna_severed():
    """Test DNA_SEVERED detection."""
    print("\n[TEST 3] DNA Severed Detection...")
    
    orphan_code = """
class OrphanAgent:
    def heal_repository(self):
        return {"status": "ok"}
"""
    tree = ast.parse(orphan_code)
    visitor = ArchitectureDNAVisitor("orphan.py")
    visitor.visit(tree)
    
    if any(v.violation_type == "DNA_SEVERED" for v in visitor.violations):
        print("✅ PASS: DNA Severed detected.")
        return True
    else:
        print("❌ FAIL: DNA Severed NOT detected.")
        return False


def test_compliant_agent():
    """Test that compliant agents pass with 0 violations."""
    print("\n[TEST 4] Compliant Agent (No Violations)...")
    
    good_code = """
class GoodAgent(SovereignBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def heal_repository(self, dry_run=True, **kwargs):
        violations = self._scan()
        return {"status": "SUCCESS", "violations_found": len(violations)}
    
    def _scan(self):
        return []
"""
    tree = ast.parse(good_code)
    
    # Run all visitors
    init_visitor = InitializationIntegrityVisitor("good.py")
    init_visitor.visit(tree)
    
    healer_visitor = HealerComplianceVisitor("good.py")
    healer_visitor.visit(tree)
    
    all_violations = init_visitor.violations + healer_visitor.violations
    
    if len(all_violations) == 0:
        print("✅ PASS: Compliant agent has 0 violations.")
        return True
    else:
        print(f"❌ FAIL: Compliant agent has violations: {[v.message for v in all_violations]}")
        return False


def test_sentinel_instantiation():
    """Test that Sentinel can be instantiated and run."""
    print("\n[TEST 5] Sentinel Instantiation...")
    
    try:
        sentinel = CanonDependencySentinelAgent()
        result = sentinel.heal_repository(dry_run=True, execute=False)
        print(f"✅ PASS: Sentinel instantiated. Status: {result.get('status')}")
        return True
    except Exception as e:
        print(f"❌ FAIL: Sentinel failed: {e}")
        return False


def run_all_tests():
    """Run all closure verification tests."""
    print("=" * 70)
    print("PHASE 16 FINAL - ARCHITECTURAL CLOSURE VERIFICATION")
    print("=" * 70)
    
    results = []
    
    results.append(("Zombie Healer Detection", test_zombie_healer()))
    results.append(("Init Bypass Detection", test_init_bypass()))
    results.append(("DNA Severed Detection", test_dna_severed()))
    results.append(("Compliant Agent (No Violations)", test_compliant_agent()))
    results.append(("Sentinel Instantiation", test_sentinel_instantiation()))
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ARCHITECTURAL CLOSURE VERIFIED - All systems operational.")
        return 0
    else:
        print("\n⚠️ CLOSURE INCOMPLETE - Review failures.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
