#!/usr/bin/env python3
"""
Test script for consolidated Gravity system
Tests both GravityValidatorAgent and GravityHealerAgent
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.GravityValidatorAgent import (
    GravityValidatorAgent,
    GravityViolation,
)
from agentic_core.L2_execution.ToolRegistry.GravityHealerAgent import GravityHealerAgent


async def test_gravity_validator():
    """Test GravityValidatorAgent detection capabilities."""
    print("=" * 80)
    print("TESTING GRAVITY VALIDATOR AGENT")
    print("=" * 80)
    
    validator = GravityValidatorAgent(project_root)
    
    # Test on a few known problematic files
    test_files = [
        project_root / "agentic_core" / "L1_cognition" / "thought_engine" / "GovernanceAgent.py",
        project_root / "agentic_core" / "L1_cognition" / "thought_engine" / "HealerAgent.py",
        project_root / "agentic_core" / "L2_execution" / "ToolRegistry" / "CodeDeduplicationAgent.py",
    ]
    
    all_violations = []
    
    for test_file in test_files:
        if not test_file.exists():
            print(f"\n⚠️  File not found: {test_file.name}")
            continue
            
        print(f"\n📄 Scanning: {test_file.relative_to(project_root)}")
        violations = await validator.detect_violations(test_file)
        
        if violations:
            print(f"   ❌ Found {len(violations)} violation(s):")
            for v in violations:
                print(f"      - Type: {v.violation_type}")
                print(f"        Line {v.line_number}: {v.import_line}")
                print(f"        Severity: {v.severity}/10")
                print(f"        Action: {v.suggested_action}")
                all_violations.append(v)
        else:
            print(f"   ✅ No violations found")
    
    print(f"\n{'=' * 80}")
    print(f"VALIDATOR SUMMARY: {len(all_violations)} total violations detected")
    print(f"{'=' * 80}\n")
    
    return all_violations


async def test_gravity_healer(violations):
    """Test GravityHealerAgent healing capabilities."""
    print("=" * 80)
    print("TESTING GRAVITY HEALER AGENT")
    print("=" * 80)
    
    if not violations:
        print("\n⚠️  No violations to heal (validator found no issues)")
        return
    
    healer = GravityHealerAgent(project_root)
    
    print(f"\n🔧 Attempting to heal {len(violations)} violation(s)...")
    print("   (DRY RUN - No actual file modifications)\n")
    
    # For testing, we'll just analyze the violations without actually healing
    for i, v in enumerate(violations[:5], 1):  # Limit to first 5 for brevity
        print(f"{i}. File: {v.file_path.name}")
        print(f"   Type: {v.violation_type}")
        print(f"   Import: {v.import_line}")
        print(f"   Suggested Action: {v.suggested_action}")
        
        if v.suggested_action == "DYNAMIC_IMPORT":
            print(f"   → Would convert to: importlib.import_module(...)")
        elif v.suggested_action == "COMMENT_OUT":
            print(f"   → Would comment out: # GRAVITY VIOLATION: {v.import_line}")
        elif v.suggested_action == "RELOCATE_FILE":
            print(f"   → Would suggest moving file to: {v.target_layer}/")
        print()
    
    if len(violations) > 5:
        print(f"   ... and {len(violations) - 5} more violations")
    
    print(f"\n{'=' * 80}")
    print(f"HEALER SUMMARY: Ready to heal {len(violations)} violations")
    print(f"{'=' * 80}\n")


async def test_full_repository_scan():
    """Test full repository scan (limited scope for demo)."""
    print("=" * 80)
    print("TESTING FULL REPOSITORY SCAN (Sample)")
    print("=" * 80)
    
    validator = GravityValidatorAgent(project_root)
    
    # Scan just L1_cognition for demo purposes
    l1_path = project_root / "agentic_core" / "L1_cognition"
    
    if not l1_path.exists():
        print("\n⚠️  L1_cognition directory not found")
        return
    
    print(f"\n📂 Scanning: {l1_path.relative_to(project_root)}")
    
    violations_by_type = {
        "intra_core": [],
        "upstream_downstream": [],
        "upward_leak": [],
    }
    
    files_scanned = 0
    
    for py_file in l1_path.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
            
        files_scanned += 1
        violations = await validator.detect_violations(py_file)
        
        for v in violations:
            violations_by_type[v.violation_type].append(v)
    
    print(f"\n📊 SCAN RESULTS:")
    print(f"   Files scanned: {files_scanned}")
    print(f"   Total violations: {sum(len(v) for v in violations_by_type.values())}")
    print(f"\n   By Type:")
    print(f"   - Intra-core violations: {len(violations_by_type['intra_core'])}")
    print(f"   - Upstream→Downstream: {len(violations_by_type['upstream_downstream'])}")
    print(f"   - Upward leaks: {len(violations_by_type['upward_leak'])}")
    
    print(f"\n{'=' * 80}\n")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CONSOLIDATED GRAVITY SYSTEM TEST")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print("=" * 80 + "\n")
    
    # Test 1: Validator on specific files
    violations = await test_gravity_validator()
    
    # Test 2: Healer analysis
    await test_gravity_healer(violations)
    
    # Test 3: Sample repository scan
    await test_full_repository_scan()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
