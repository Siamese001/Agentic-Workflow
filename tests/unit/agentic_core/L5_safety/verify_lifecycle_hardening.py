#!/usr/bin/env python3
"""
Verify Lifecycle Hardening - Tests for Sovereign Lifecycle Guard.

Tests:
1. Good Agent - Compliant agent should pass with 0 violations
2. Init Hijacker - Missing super().__init__ should be detected
3. Zombie Healer - No-op heal_repository should be detected
4. Orchestrator Gate - Mission should abort on critical violations

Usage:
    python tests/verify_lifecycle_hardening.py
"""

from __future__ import annotations
import ast
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.CanonDependencySentinelAgent import (
    InitializationIntegrityVisitor,
    HealerComplianceVisitor,
    ArchitectureDNAVisitor,
)


# --- MOCK AGENT CODE ---

GOOD_AGENT_CODE = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestGoodAgent(SovereignBaseAgent):
    def __init__(self, name: str = "test", **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        print("Healing...")
        violations = self._scan_for_issues()
        return {"status": "SUCCESS", "violations_found": len(violations)}

    def _scan_for_issues(self):
        return []
"""

BAD_INIT_CODE = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestBadInitAgent(SovereignBaseAgent):
    def __init__(self, name: str, **kwargs):
        # VIOLATION: Missing super().__init__
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

NO_KWARGS_CODE = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestNoKwargsAgent(SovereignBaseAgent):
    def __init__(self, name: str):
        super().__init__()  # VIOLATION: Missing **kwargs propagation
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

ZOMBIE_HEALER_CODE = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestZombieAgent(SovereignBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        pass  # VIOLATION: No-op stub
"""

ZOMBIE_HEALER_RETURN_CODE = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestZombieReturnAgent(SovereignBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "skipped"}  # VIOLATION: Just returns dict, no logic
"""

DNA_SEVERED_CODE = """
class TestOrphanAgent:
    '''Agent without SovereignBaseAgent inheritance'''
    def __init__(self):
        pass

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""


def test_good_agent():
    """Test 1: Compliant Agent should pass with 0 violations."""
    print("\n[TEST 1] Scanning Compliant Agent...")

    tree = ast.parse(GOOD_AGENT_CODE)

    # Run Init Integrity
    init_visitor = InitializationIntegrityVisitor("TestGoodAgent.py")
    init_visitor.visit(tree)

    # Run Healer Compliance
    healer_visitor = HealerComplianceVisitor("TestGoodAgent.py")
    healer_visitor.visit(tree)

    all_violations = init_visitor.violations + healer_visitor.violations

    if len(all_violations) == 0:
        print("✅ PASS: No violations found in compliant agent.")
        return True
    else:
        print(f"❌ FAIL: Unexpected violations: {[v.message for v in all_violations]}")
        return False


def test_bad_init():
    """Test 2: Init Hijacker should be detected."""
    print("\n[TEST 2] Scanning Initialization Hijacker...")

    tree = ast.parse(BAD_INIT_CODE)
    visitor = InitializationIntegrityVisitor("TestBadInitAgent.py")
    visitor.visit(tree)

    init_violations = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]

    if len(init_violations) > 0:
        print(f"✅ PASS: Detected INIT_BYPASS. Message: {init_violations[0].message}")
        return True
    else:
        print("❌ FAIL: Failed to detect missing super().__init__.")
        return False


def test_no_kwargs():
    """Test 3: Missing **kwargs propagation should be detected."""
    print("\n[TEST 3] Scanning Missing **kwargs Agent...")

    tree = ast.parse(NO_KWARGS_CODE)
    visitor = InitializationIntegrityVisitor("TestNoKwargsAgent.py")
    visitor.visit(tree)

    init_violations = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]

    if len(init_violations) > 0:
        print(f"✅ PASS: Detected missing **kwargs. Message: {init_violations[0].message}")
        return True
    else:
        print("❌ FAIL: Failed to detect missing **kwargs propagation.")
        return False


def test_zombie_healer_pass():
    """Test 4: Zombie Healer (pass only) should be detected."""
    print("\n[TEST 4] Scanning Zombie Healer (pass)...")

    tree = ast.parse(ZOMBIE_HEALER_CODE)
    visitor = HealerComplianceVisitor("TestZombieAgent.py")
    visitor.visit(tree)

    zombie_violations = [v for v in visitor.violations if v.violation_type == "ZOMBIE_HEALER"]

    if len(zombie_violations) > 0:
        print(f"✅ PASS: Detected ZOMBIE_HEALER. Message: {zombie_violations[0].message}")
        return True
    else:
        print("❌ FAIL: Failed to detect no-op heal_repository.")
        return False


def test_zombie_healer_return():
    """Test 5: Zombie Healer (return dict only) should be detected."""
    print("\n[TEST 5] Scanning Zombie Healer (return dict)...")

    tree = ast.parse(ZOMBIE_HEALER_RETURN_CODE)
    visitor = HealerComplianceVisitor("TestZombieReturnAgent.py")
    visitor.visit(tree)

    zombie_violations = [v for v in visitor.violations if v.violation_type == "ZOMBIE_HEALER"]

    if len(zombie_violations) > 0:
        print(f"✅ PASS: Detected ZOMBIE_HEALER. Message: {zombie_violations[0].message}")
        return True
    else:
        print("❌ FAIL: Failed to detect return-only heal_repository.")
        return False


def test_dna_severed():
    """Test 6: Orphan Agent (no L0 foundation) should be detected."""
    print("\n[TEST 6] Scanning Orphan Agent (DNA Severed)...")

    tree = ast.parse(DNA_SEVERED_CODE)
    visitor = ArchitectureDNAVisitor("TestOrphanAgent.py")
    visitor.visit(tree)

    severed_violations = [v for v in visitor.violations if v.violation_type == "DNA_SEVERED"]

    if len(severed_violations) > 0:
        print(f"✅ PASS: Detected DNA_SEVERED. Message: {severed_violations[0].message}")
        return True
    else:
        print("❌ FAIL: Failed to detect orphan agent.")
        return False


def run_all_tests():
    """Run all lifecycle hardening tests."""
    print("=" * 70)
    print("SOVEREIGN LIFECYCLE HARDENING - VERIFICATION TESTS")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Test 1: Good Agent (Compliant)", test_good_agent()))
    results.append(("Test 2: Bad Init (Missing super())", test_bad_init()))
    results.append(("Test 3: No **kwargs Propagation", test_no_kwargs()))
    results.append(("Test 4: Zombie Healer (pass)", test_zombie_healer_pass()))
    results.append(("Test 5: Zombie Healer (return dict)", test_zombie_healer_return()))
    results.append(("Test 6: DNA Severed (Orphan)", test_dna_severed()))

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
        print("\n🎉 ALL TESTS PASSED - Sovereign Lifecycle Guard is fully operational.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Review implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
