#!/usr/bin/env python3
"""
Debug Critical Complexity Enforcement
Fix the one remaining enforcement issue
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from agentic_core.config.adg_template_enforcement_config import ENFORCEMENT_RULES, get_enforcement_template


def debug_critical_complexity():
    """Debug why critical complexity enforcement isn't working."""

    print("🔍 DEBUGGING CRITICAL COMPLEXITY ENFORCEMENT")
    print("=" * 60)

    # Test critical complexity enforcement
    step_config = {
        'type': 'implementation',
        'complexity': 'critical',
        'files': ['file.py']
    }

    print(f"Testing: {step_config['type']} with {step_config['complexity']} complexity")

    # Check enforcement rules
    print("\n📋 Enforcement Rules:")
    print(f"   Critical Template: {ENFORCEMENT_RULES['complexity_enforcement']['critical']}")

    # Check if task type is in direct ADG tasks
    in_direct = step_config['type'] in ENFORCEMENT_RULES['direct_adg_tasks']
    print(f"   In Direct ADG Tasks: {in_direct}")

    # Check if task type is in SWE task mapping
    in_swe = step_config['type'] in ENFORCEMENT_RULES['swe_task_mapping']
    print(f"   In SWE Task Mapping: {in_swe}")

    if in_swe:
        print(f"   SWE Mapped Template: {ENFORCEMENT_RULES['swe_task_mapping'][step_config['type']]}")

    # Get enforcement template
    enforced_template = get_enforcement_template(step_config['type'], step_config)
    print("\n🎯 Enforcement Result:")
    print("   Expected: SWE_SYSTEM_RESTRUCTURING")
    print(f"   Actual: {enforced_template}")
    print(f"   Match: {enforced_template == 'SWE_SYSTEM_RESTRUCTURING'}")

    # Debug the enforcement logic step by step
    print("\n🔧 Step-by-Step Logic:")

    # Step 1: Check direct ADG tasks
    if step_config['type'] in ENFORCEMENT_RULES['direct_adg_tasks']:
        print("   1. ✅ Direct ADG task matched")
        print(f"      Would return: {ENFORCEMENT_RULES['direct_adg_tasks'][step_config['type']]}")
    else:
        print("   1. ❌ Direct ADG task not matched")

    # Step 2: Check SWE task mapping
    if step_config['type'] in ENFORCEMENT_RULES['swe_task_mapping']:
        print("   2. ✅ SWE task mapping matched")
        print(f"      Would return: {ENFORCEMENT_RULES['swe_task_mapping'][step_config['type']]}")
        print("   ⚠️  This is PREVENTING complexity enforcement!")
        print("   ⚠️  SWE mapping takes precedence over complexity rules")
    else:
        print("   2. ❌ SWE task mapping not matched")

    # Step 3: Check complexity
    if step_config and step_config.get('complexity', 'medium').lower() == 'critical':
        print("   3. ✅ Critical complexity detected")
        print(f"      Would return: {ENFORCEMENT_RULES['complexity_enforcement']['critical']}")
        print("   ❌ But never reached due to SWE mapping precedence!")
    else:
        print("   3. ❌ Critical complexity not detected")

    # The issue is precedence order!
    print("\n🎯 ROOT CAUSE IDENTIFIED:")
    print("   ❌ SWE task mapping has HIGHER precedence than complexity enforcement")
    print("   ❌ 'implementation' is mapped to 'SWE_DEPENDENCY_GRAPH_ANALYSIS' in SWE mapping")
    print("   ❌ Complexity rules are checked AFTER SWE mapping")
    print("   ❌ So critical complexity never gets a chance to enforce")

    # Solution: Change precedence order
    print("\n💡 SOLUTION:")
    print("   ✅ Check complexity enforcement BEFORE SWE task mapping")
    print("   ✅ Critical complexity should override all other rules")

    return enforced_template

if __name__ == "__main__":
    debug_critical_complexity()
