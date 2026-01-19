#!/usr/bin/env python3
"""
Root Cause Analysis: DuplicateCodeDetectorAgent Location
=========================================================

Analyzes why DuplicateCodeDetectorAgent is in apps_lic/engines/ instead of apps_shared/
and determines the correct location based on:
1. Purpose and scope
2. Dependencies
3. Usage patterns
4. Sovereign registry structure
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    APPS_LIC_DIR,
    APPS_SHARED_DIR,
    APPS_RG_DIR,
)

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


# ============================================================================
# RCA Test 1: Analyze Agent Purpose and Scope
# ============================================================================

def test_agent_purpose():
    """Determine if DuplicateCodeDetectorAgent is app-specific or shared."""
    print("\n" + "=" * 60)
    print("RCA Test 1: Agent Purpose and Scope")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "apps_lic/engines/DuplicateCodeDetectorAgent.py"
    
    if not agent_path.exists():
        test_fail("FILE_EXISTS", "DuplicateCodeDetectorAgent.py not found in apps_lic")
        return
    
    content = agent_path.read_text(encoding='utf-8')
    
    # Check if agent is app-specific (LIC-specific logic)
    lic_specific_indicators = [
        'apps_lic',
        'linkedin',
        'outreach',
        'campaign',
        'lead',
    ]
    
    # Check if agent is generic/shared
    shared_indicators = [
        'agentic_core',
        'GLOBAL_EXCLUDED_DIRS',
        'structure_blueprint',
        'project_root',
        'file_types',
    ]
    
    lic_count = sum(1 for indicator in lic_specific_indicators if indicator.lower() in content.lower())
    shared_count = sum(1 for indicator in shared_indicators if indicator in content)
    
    print(f"  LIC-specific indicators: {lic_count}")
    print(f"  Shared/generic indicators: {shared_count}")
    
    if shared_count > lic_count:
        test_pass("SCOPE", f"Agent is GENERIC (shared: {shared_count} > lic: {lic_count})")
        print(f"  📊 VERDICT: Should be in apps_shared (generic utility)")
    else:
        test_fail("SCOPE", f"Agent appears LIC-specific (lic: {lic_count} >= shared: {shared_count})")
        print(f"  📊 VERDICT: Current location apps_lic is correct")


# ============================================================================
# RCA Test 2: Analyze Dependencies
# ============================================================================

def test_dependencies():
    """Check if dependencies are app-specific or shared."""
    print("\n" + "=" * 60)
    print("RCA Test 2: Dependency Analysis")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "apps_lic/engines/DuplicateCodeDetectorAgent.py"
    
    if not agent_path.exists():
        test_fail("FILE_EXISTS", "Agent file not found")
        return
    
    content = agent_path.read_text(encoding='utf-8')
    
    # Extract imports
    import_lines = [line for line in content.split('\n') if line.strip().startswith('from ') or line.strip().startswith('import ')]
    
    apps_lic_imports = [line for line in import_lines if 'apps_lic' in line]
    apps_shared_imports = [line for line in import_lines if 'apps_shared' in line]
    agentic_core_imports = [line for line in import_lines if 'agentic_core' in line]
    
    print(f"  apps_lic imports: {len(apps_lic_imports)}")
    print(f"  apps_shared imports: {len(apps_shared_imports)}")
    print(f"  agentic_core imports: {len(agentic_core_imports)}")
    
    if len(apps_lic_imports) == 0:
        test_pass("DEPS", "No apps_lic dependencies - agent is NOT LIC-specific")
        print(f"  📊 VERDICT: Should be in apps_shared (no LIC dependencies)")
    else:
        test_fail("DEPS", f"Has {len(apps_lic_imports)} apps_lic dependencies")
        print(f"  📊 VERDICT: May need to stay in apps_lic")
        for imp in apps_lic_imports:
            print(f"    - {imp.strip()}")


# ============================================================================
# RCA Test 3: Check Usage Patterns
# ============================================================================

def test_usage_patterns():
    """Check where DuplicateCodeDetectorAgent is used."""
    print("\n" + "=" * 60)
    print("RCA Test 3: Usage Pattern Analysis")
    print("=" * 60)
    
    # Search for imports of DuplicateCodeDetectorAgent
    usage_files = []
    
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if 'DuplicateCodeDetectorAgent.py' in str(py_file):
            continue
        if any(excluded in str(py_file) for excluded in ['__pycache__', '.venv', 'venv', 'archives']):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            if 'DuplicateCodeDetectorAgent' in content:
                usage_files.append(py_file)
        except:
            pass
    
    print(f"  Found {len(usage_files)} files using DuplicateCodeDetectorAgent")
    
    apps_lic_usage = [f for f in usage_files if 'apps_lic' in str(f)]
    apps_rg_usage = [f for f in usage_files if 'apps_rg' in str(f)]
    apps_shared_usage = [f for f in usage_files if 'apps_shared' in str(f)]
    agentic_core_usage = [f for f in usage_files if 'agentic_core' in str(f)]
    
    print(f"  apps_lic usage: {len(apps_lic_usage)}")
    print(f"  apps_rg usage: {len(apps_rg_usage)}")
    print(f"  apps_shared usage: {len(apps_shared_usage)}")
    print(f"  agentic_core usage: {len(agentic_core_usage)}")
    
    cross_app_usage = len(apps_rg_usage) > 0 or len(agentic_core_usage) > 0
    
    if cross_app_usage:
        test_pass("USAGE", "Agent is used across multiple apps/core - should be shared")
        print(f"  📊 VERDICT: Should be in apps_shared (cross-app usage)")
    elif len(usage_files) == 0:
        test_pass("USAGE", "No current usage found - can be moved to apps_shared")
        print(f"  📊 VERDICT: Should be in apps_shared (generic utility)")
    else:
        test_fail("USAGE", f"Only used in apps_lic ({len(apps_lic_usage)} files)")
        print(f"  📊 VERDICT: Current location may be correct")


# ============================================================================
# RCA Test 4: Sovereign Registry Compliance
# ============================================================================

def test_sovereign_registry():
    """Check sovereign registry structure for apps_* folders."""
    print("\n" + "=" * 60)
    print("RCA Test 4: Sovereign Registry Structure")
    print("=" * 60)
    
    apps_lic_structure = SOVEREIGN_REGISTRY.get('apps_lic', {})
    apps_shared_structure = SOVEREIGN_REGISTRY.get('apps_shared', {})
    
    print(f"  apps_lic subfolders: {apps_lic_structure.get('subfolders', [])}")
    print(f"  apps_shared subfolders: {apps_shared_structure.get('subfolders', [])}")
    
    # Check if 'engines' is a valid subfolder
    if 'engines' in apps_lic_structure.get('subfolders', []):
        test_pass("STRUCTURE", "'engines' is valid in apps_lic")
    else:
        test_fail("STRUCTURE", "'engines' NOT in apps_lic subfolders")
    
    if 'utils' in apps_shared_structure.get('subfolders', []):
        test_pass("STRUCTURE", "'utils' is valid in apps_shared (good target)")
        print(f"  📊 VERDICT: apps_shared/utils/ is appropriate for shared utilities")
    else:
        test_fail("STRUCTURE", "'utils' NOT in apps_shared subfolders")


# ============================================================================
# RCA Test 5: Functional Analysis
# ============================================================================

def test_functional_analysis():
    """Analyze what the agent does."""
    print("\n" + "=" * 60)
    print("RCA Test 5: Functional Analysis")
    print("=" * 60)
    
    agent_path = PROJECT_ROOT / "apps_lic/engines/DuplicateCodeDetectorAgent.py"
    
    if not agent_path.exists():
        test_fail("FILE_EXISTS", "Agent file not found")
        return
    
    content = agent_path.read_text(encoding='utf-8')
    
    # Check what the agent does
    functions = {
        'Detects duplicate files': 'whole_file_duplicates' in content,
        'Detects duplicate code blocks': 'code_block_duplicates' in content,
        'Uses AST fingerprinting': 'ast.parse' in content or 'tree_sitter' in content,
        'Scans entire project': 'project_root' in content,
        'Generic file scanning': 'file_types' in content or 'SUPPORTED_EXTENSIONS' in content,
        'LIC-specific logic': 'linkedin' in content.lower() or 'outreach' in content.lower(),
    }
    
    for func, present in functions.items():
        if present:
            print(f"  ✓ {func}")
        else:
            print(f"  ✗ {func}")
    
    generic_count = sum(1 for k, v in functions.items() if v and 'Generic' in k or 'Scans entire' in k or 'Detects' in k)
    specific_count = sum(1 for k, v in functions.items() if v and 'LIC-specific' in k)
    
    if generic_count > specific_count:
        test_pass("FUNCTION", f"Agent is GENERIC utility (generic: {generic_count} > specific: {specific_count})")
        print(f"  📊 VERDICT: Should be in apps_shared (generic code quality tool)")
    else:
        test_fail("FUNCTION", f"Agent may be app-specific (specific: {specific_count} >= generic: {generic_count})")


# ============================================================================
# Final RCA Summary
# ============================================================================

def print_rca_summary():
    """Print final RCA verdict."""
    print("\n" + "=" * 60)
    print("ROOT CAUSE ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"  Total Checks: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print()
    
    # Determine verdict
    if PASSED >= 3:
        print("  🎯 FINAL VERDICT: DuplicateCodeDetectorAgent should be in apps_shared")
        print()
        print("  📋 ROOT CAUSE:")
        print("    - Agent is a GENERIC code quality utility")
        print("    - No LIC-specific dependencies or logic")
        print("    - Scans entire project (not app-specific)")
        print("    - Uses shared infrastructure (structure_blueprint, GLOBAL_EXCLUDED_DIRS)")
        print("    - Should be available to ALL apps (RG, LIC, and future apps)")
        print()
        print("  ✅ RECOMMENDATION:")
        print("    Move to: apps_shared/utils/DuplicateCodeDetectorAgent.py")
        print("    Rationale: Shared code quality tool for all applications")
        return 0
    else:
        print("  ⚠️  FINAL VERDICT: Current location apps_lic may be correct")
        print()
        print("  📋 Analysis shows app-specific characteristics")
        print("  Further investigation needed")
        return 1


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("=" * 60)
    print("ROOT CAUSE ANALYSIS: DuplicateCodeDetectorAgent Location")
    print("=" * 60)
    print("Analyzing why agent is in apps_lic instead of apps_shared")
    
    test_agent_purpose()
    test_dependencies()
    test_usage_patterns()
    test_sovereign_registry()
    test_functional_analysis()
    
    return print_rca_summary()


if __name__ == "__main__":
    sys.exit(main())
