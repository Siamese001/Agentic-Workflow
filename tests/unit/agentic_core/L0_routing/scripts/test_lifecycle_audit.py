#!/usr/bin/env python3
"""
Lifecycle Audit Script - Validates Sovereign Lifecycle Guard hardening.

Tests:
- DNA-01: Compliant Agent (correct super().__init__(**kwargs))
- DNA-02: Init Hijacking (missing super() or **kwargs)
- DNA-03: Shadow Mixin (inherits mixin but never calls its methods) [Future]
- DNA-04: Zombie Healer (heal_repository returns skipped with empty body) [Future]

Usage:
    python scripts/lifecycle_audit.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# from agentic_core.L5_safety.validators.CanonDependencySentinelAgent import (
#     ArchitectureDNAVisitor,
#     InitializationIntegrityVisitor,
# )

# Test Cases
COMPLIANT_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class CompliantAgent(SovereignBaseAgent):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS", "violations_found": 0}
"""

INIT_HIJACKING_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class ZombieAgent(SovereignBaseAgent):
    def __init__(self, some_arg):
        self.some_arg = some_arg
        # Missing super().__init__(**kwargs)

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

INIT_NO_KWARGS_AGENT = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class NoKwargsAgent(SovereignBaseAgent):
    def __init__(self, name: str):
        super().__init__()  # Missing **kwargs propagation
        self.name = name

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""

DNA_SEVERED_AGENT = """
class OrphanAgent:
    '''Agent without SovereignBaseAgent inheritance'''
    def __init__(self):
        pass

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        return {"status": "SUCCESS"}
"""


def test_init_gate_compliant():
    """DNA-01: Compliant Agent should pass with 0 violations."""
    if "InitializationIntegrityVisitor" not in dir():
        pytest.fail("InitializationIntegrityVisitor not available (import commented out)")
    tree = ast.parse(COMPLIANT_AGENT)
    visitor = InitializationIntegrityVisitor("test_compliant.py")
    visitor.visit(tree)

    if len(visitor.violations) == 0:
        print("✅ DNA-01 PASS: Compliant agent correctly identified as valid.")
        return True
    else:
        print(
            f"❌ DNA-01 FAIL: Compliant agent incorrectly flagged. Violations: {[v.message for v in visitor.violations]}",
        )
        return False


def test_init_gate_hijacking():
    """DNA-02: Init Hijacking should be detected."""
    if "InitializationIntegrityVisitor" not in dir():
        pytest.fail("InitializationIntegrityVisitor not available (import commented out)")
    tree = ast.parse(INIT_HIJACKING_AGENT)
    visitor = InitializationIntegrityVisitor("test_hijacking.py")
    visitor.visit(tree)

    init_bypasses = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]

    if len(init_bypasses) > 0:
        print(f"✅ DNA-02 PASS: Init hijacking detected. Message: {init_bypasses[0].message}")
        return True
    else:
        print("❌ DNA-02 FAIL: Init hijacking NOT detected.")
        return False


def test_init_gate_no_kwargs():
    """DNA-02b: Init without **kwargs propagation should be detected."""
    if "InitializationIntegrityVisitor" not in dir():
        pytest.fail("InitializationIntegrityVisitor not available (import commented out)")
    tree = ast.parse(INIT_NO_KWARGS_AGENT)
    visitor = InitializationIntegrityVisitor("test_no_kwargs.py")
    visitor.visit(tree)

    init_bypasses = [v for v in visitor.violations if v.violation_type == "INIT_BYPASS"]

    if len(init_bypasses) > 0:
        print(f"✅ DNA-02b PASS: Missing **kwargs detected. Message: {init_bypasses[0].message}")
        return True
    else:
        print("❌ DNA-02b FAIL: Missing **kwargs NOT detected.")
        return False


def test_dna_severed():
    """DNA-SEVERED: Agent without L0 foundation should be detected."""
    if "ArchitectureDNAVisitor" not in dir():
        pytest.fail("ArchitectureDNAVisitor not available (import commented out)")
    tree = ast.parse(DNA_SEVERED_AGENT)
    visitor = ArchitectureDNAVisitor("test_severed.py")
    visitor.visit(tree)

    severed = [v for v in visitor.violations if v.violation_type == "DNA_SEVERED"]

    if len(severed) > 0:
        print(f"✅ DNA-SEVERED PASS: Orphan agent detected. Message: {severed[0].message}")
        return True
    else:
        print("❌ DNA-SEVERED FAIL: Orphan agent NOT detected.")
        return False


def run_all_tests():
    """Run all lifecycle audit tests."""
    print("=" * 60)
    print("SOVEREIGN LIFECYCLE GUARD - AUDIT TESTS")
    print("=" * 60)
    print()

    results = []

    # Run tests
    results.append(("DNA-01: Compliant Agent", test_init_gate_compliant()))
    results.append(("DNA-02: Init Hijacking", test_init_gate_hijacking()))
    results.append(("DNA-02b: No **kwargs", test_init_gate_no_kwargs()))
    results.append(("DNA-SEVERED: Orphan Agent", test_dna_severed()))

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Sovereign Lifecycle Guard is operational.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Review implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
