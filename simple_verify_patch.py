#!/usr/bin/env python3
"""
Simple Verification Script for Universal Healing Implementation
Quick verification that the patch is correctly applied.
"""

import sys
import re
from pathlib import Path

def verify_patch():
    """Verify that the Universal Healing patch is correctly applied."""
    print("🔍 Universal Healing Patch Verification")
    print("=" * 50)
    
    project_root = Path.cwd()
    execute_ssot_path = project_root / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py"
    
    if not execute_ssot_path.exists():
        print("❌ FAIL: execute_ssot.py not found")
        return False
    
    # Read the file
    try:
        content = execute_ssot_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ FAIL: Could not read execute_ssot.py: {e}")
        return False
    
    # Check for Universal Healing comment
    if "[UNIVERSAL HEALING]" not in content:
        print("❌ FAIL: Universal Healing patch not found")
        return False
    else:
        print("✅ PASS: Universal Healing patch detected")
    
    # Check for Phase 2.5 Sovereignty Enforcement
    if "Phase 2.5: Sovereignty Enforcement" not in content:
        print("❌ FAIL: Phase 2.5 Sovereignty Enforcement not found")
        return False
    else:
        print("✅ PASS: Phase 2.5 Sovereignty Enforcement detected")
    
    # Check for Pascal agent healing call
    if "pascal.heal_repository(target_territory=territory, dry_run=False)" not in content:
        print("❌ FAIL: Pascal agent healing call not found")
        return False
    else:
        print("✅ PASS: Pascal agent healing call detected")
    
    # Check for dry-run safety
    if "if not dry_run:" not in content:
        print("❌ FAIL: Dry-run safety check not found")
        return False
    else:
        print("✅ PASS: Dry-run safety check detected")
    
    # Check for all required agents in imports
    required_agents = [
        "PascalSovereigntyAgent",
        "RootHygieneAgent"
    ]
    
    for agent in required_agents:
        if agent not in content:
            print(f"❌ FAIL: {agent} not found in imports")
            return False
        else:
            print(f"✅ PASS: {agent} found in imports")
    
    # Check that the patch is in the right location (main execution loop)
    main_execution_pattern = r"for territory in targets:.*?if not dry_run:.*?pascal = agents\['pascal_sovereignty'\]"
    if not re.search(main_execution_pattern, content, re.DOTALL):
        print("❌ FAIL: Universal Healing logic not in main execution loop")
        return False
    else:
        print("✅ PASS: Universal Healing logic in correct location")
    
    print("\n" + "=" * 50)
    print("🎉 PATCH VERIFICATION COMPLETE")
    print("=" * 50)
    print("✅ Universal Healing patch is CORRECTLY APPLIED")
    print("\nKey Features Verified:")
    print("- Universal Healing comment block")
    print("- Phase 2.5 Sovereignty Enforcement")
    print("- Pascal agent heal_repository call")
    print("- Dry-run safety mechanism")
    print("- All required agents imported")
    print("- Logic in main execution loop")
    
    return True

def test_imports():
    """Test that the patched module can be imported."""
    print("\n🧪 Module Import Test")
    print("-" * 30)
    
    try:
        project_root = Path.cwd()
        sys.path.insert(0, str(project_root))
        
        from agentic_core.L0_maintenance.scripts.execute_ssot import (
            AutonomousDecisionEngine,
            RuntimeStateManager
        )
        
        print("✅ PASS: Module imports successfully")
        
        # Test decision engine
        decision_engine = AutonomousDecisionEngine(enable_llm=False)
        confidence = decision_engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=['NAMING', 'HIERARCHY'],
            territory='prompt_governance'
        )
        
        print(f"✅ PASS: Decision engine working (confidence: {confidence.value:.2f})")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Import test failed: {e}")
        return False

if __name__ == "__main__":
    patch_ok = verify_patch()
    imports_ok = test_imports()
    
    if patch_ok and imports_ok:
        print("\n🎉 ALL VERIFICATIONS PASSED")
        print("Universal Healing is READY FOR USE!")
        sys.exit(0)
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        sys.exit(1)
