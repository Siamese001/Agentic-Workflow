#!/usr/bin/env python3
"""
Batch 1 Mass Remediation Verification Suite

Verifies:
- T-01: Rogue Bypass - LocationHealerAgent respects SOVEREIGN_AUTO_APPROVE
- T-02: Signal Saturation - HistorianAgent accepts **kwargs
- T-03: Safety Context - CodeDeduplicationAgent respects sovereign context

100% pass required.
"""
from __future__ import annotations

import os
import sys
import ast
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_t01_rogue_bypass():
    """T-01: LocationHealerAgent respects SOVEREIGN_AUTO_APPROVE."""
    print("\n" + "=" * 60)
    print("T-01: Rogue Bypass Test")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationHealerAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    
    # Check for SOVEREIGN_AUTO_APPROVE in _prompt_user_for_archive_approval
    checks = [
        ("SOVEREIGN_AUTO_APPROVE" in content, "SOVEREIGN_AUTO_APPROVE check present"),
        ("ARCHIVE_BATCH_ACCEPT" in content, "ARCHIVE_BATCH_ACCEPT check present"),
        ('input("Approve archive' not in content, "Direct input() call removed"),
        ("gatekeeper.safe_operation" in content, "Gatekeeper delegation present"),
    ]
    
    passed = True
    for check, desc in checks:
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"  {status}: {desc}")
        if not check:
            passed = False
    
    return passed


def test_t02_signal_saturation():
    """T-02: HistorianAgent accepts **kwargs without TypeError."""
    print("\n" + "=" * 60)
    print("T-02: Signal Saturation Test")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "agentic_core/L2_execution/tool_registry/HistorianAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    
    passed = True
    found_heal = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
            found_heal = True
            has_kwargs = node.args.kwarg is not None
            
            if has_kwargs:
                print(f"  ✅ PASS: heal_repository has **kwargs")
            else:
                print(f"  ❌ FAIL: heal_repository missing **kwargs")
                passed = False
    
    if not found_heal:
        print(f"  ❌ FAIL: heal_repository method not found")
        passed = False
    
    # Verify it can be called with custom_flag
    print("  Testing signature acceptance...")
    try:
        # Parse and verify signature accepts arbitrary kwargs
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
                if node.args.kwarg:
                    print(f"  ✅ PASS: Can accept custom_flag='TEST' via **{node.args.kwarg.arg}")
                break
    except Exception as e:
        print(f"  ❌ FAIL: Signature test error: {e}")
        passed = False
    
    return passed


def test_t03_safety_context():
    """T-03: CodeDeduplicationAgent respects SOVEREIGN_AUTO_APPROVE."""
    print("\n" + "=" * 60)
    print("T-03: Safety Context Test")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/CodeDeduplicationAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    
    checks = [
        ("SOVEREIGN_AUTO_APPROVE" in content, "SOVEREIGN_AUTO_APPROVE check present"),
        ("resolve_duplicates_safely" in content, "resolve_duplicates_safely method exists"),
    ]
    
    # Check heal_repository has **kwargs
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
            has_kwargs = node.args.kwarg is not None
            checks.append((has_kwargs, "heal_repository has **kwargs"))
            break
    
    passed = True
    for check, desc in checks:
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"  {status}: {desc}")
        if not check:
            passed = False
    
    return passed


def test_governance_agent_remediation():
    """Verify GovernanceAgent input() removal."""
    print("\n" + "=" * 60)
    print("T-04: GovernanceAgent Remediation Test")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/GovernanceAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    
    checks = [
        ("SOVEREIGN_AUTO_APPROVE" in content, "SOVEREIGN_AUTO_APPROVE check present"),
        ('input("Approve move' not in content, "Direct input() call removed"),
        ("gatekeeper.safe_operation" in content, "Gatekeeper delegation present"),
    ]
    
    passed = True
    for check, desc in checks:
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"  {status}: {desc}")
        if not check:
            passed = False
    
    return passed


def test_strategic_planner_remediation():
    """Verify StrategicPlannerAgent has **kwargs."""
    print("\n" + "=" * 60)
    print("T-05: StrategicPlannerAgent Remediation Test")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "agentic_core/L2_execution/tool_registry/StrategicPlannerAgent.py"
    content = agent_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    
    passed = True
    found_heal = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
            found_heal = True
            has_kwargs = node.args.kwarg is not None
            
            if has_kwargs:
                print(f"  ✅ PASS: heal_repository has **kwargs")
            else:
                print(f"  ❌ FAIL: heal_repository missing **kwargs")
                passed = False
    
    if not found_heal:
        print(f"  ❌ FAIL: heal_repository method not found")
        passed = False
    
    return passed


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("BATCH 1 MASS REMEDIATION VERIFICATION SUITE")
    print("=" * 70)
    
    results = {
        "T-01 Rogue Bypass": test_t01_rogue_bypass(),
        "T-02 Signal Saturation": test_t02_signal_saturation(),
        "T-03 Safety Context": test_t03_safety_context(),
        "T-04 GovernanceAgent": test_governance_agent_remediation(),
        "T-05 StrategicPlannerAgent": test_strategic_planner_remediation(),
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Batch 1 Remediation Verified")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
