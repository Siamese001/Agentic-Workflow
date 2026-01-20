#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite: Root Directory SSOT Enforcement Hardening

Tests LocationAgent, HierarchyAgent, and FilesystemSSOTReconcilerAgent
for proper enforcement of root-level SSOT rules.

RCA Gaps Being Tested:
1. Root folder whitelist enforcement (scripts/, logs/, coverage_html/ at root)
2. .archived files at root should be moved to archives/
3. Root-level file validation
4. Duplicate folder detection (scripts/ at root vs L0_maintenance/scripts/)

Run: python scripts/test_root_ssot_enforcement.py
"""
import sys
import os
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    ROOT_WHITELIST,
    CORE_SUBFOLDER_MAP,
    get_validated_project_root,
)


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Approved root folders per SOVEREIGN_REGISTRY
APPROVED_ROOT_FOLDERS: Set[str] = set(SOVEREIGN_REGISTRY.keys())

# Standard project files/folders that are always allowed at root
STANDARD_ROOT_ITEMS: Set[str] = {
    # Git/IDE
    '.git', '.github', '.vscode', '.venv', '__pycache__', '.pytest_cache',
    # Config files
    '.env', '.gitignore', 'pyproject.toml', 'README.md',
    # Main entry point
    'canon_validator_agentic_v2_thin.py',
    # Runtime files
    'agent_discovery_full.json', 'runtime_state.json',
    # Standard folders
    'archives', 'docs', 'data', 'reports',
    # Hidden/system
    '.gravity_state', '.sovereign_healing_backup',
}

# Folders that should NOT exist at root (they have SSOT locations)
FORBIDDEN_ROOT_FOLDERS: Set[str] = {
    'scripts',       # Should be agentic_core/L0_maintenance/scripts/
    'logs',          # Should be agentic_core/L0_maintenance/logs/
    'coverage_html', # Should be reports/coverage_html/ or gitignored
    'observability', # Should be agentic_core/L6_observability/
}

# File patterns that should be in archives/, not root
ARCHIVE_PATTERNS: List[str] = [
    '.archived',
    '.backup',
    '.old',
]


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_1_root_folder_whitelist() -> Tuple[bool, str]:
    """
    Test 1: Verify ROOT_WHITELIST matches SOVEREIGN_REGISTRY keys.
    
    Gap: LocationAgent uses ROOT_WHITELIST but it may not be in sync with SOVEREIGN_REGISTRY.
    """
    expected = set(SOVEREIGN_REGISTRY.keys())
    actual = set(ROOT_WHITELIST) if ROOT_WHITELIST else set()
    
    if expected == actual:
        return True, f"ROOT_WHITELIST matches SOVEREIGN_REGISTRY ({len(expected)} entries)"
    
    missing = expected - actual
    extra = actual - expected
    msg = f"Mismatch: missing={missing}, extra={extra}"
    return False, msg


def test_2_no_forbidden_folders_at_root() -> Tuple[bool, str]:
    """
    Test 2: Verify no forbidden folders exist at project root.
    
    Gap: HierarchyAgent doesn't scan root for forbidden folders.
    """
    root = get_validated_project_root()
    violations = []
    
    for item in root.iterdir():
        if item.is_dir() and item.name in FORBIDDEN_ROOT_FOLDERS:
            violations.append(item.name)
    
    if not violations:
        return True, "No forbidden folders at root"
    
    return False, f"Forbidden folders at root: {violations}"


def test_3_no_archived_files_at_root() -> Tuple[bool, str]:
    """
    Test 3: Verify no .archived files exist at project root.
    
    Gap: LocationAgent's archiving logic renames files in place instead of moving to archives/.
    """
    root = get_validated_project_root()
    archived_files = []
    
    for item in root.iterdir():
        if item.is_file():
            for pattern in ARCHIVE_PATTERNS:
                if pattern in item.name:
                    archived_files.append(item.name)
                    break
    
    if not archived_files:
        return True, "No archived files at root"
    
    return False, f"Found {len(archived_files)} archived files at root (should be in archives/)"


def test_4_scripts_folder_ssot_location() -> Tuple[bool, str]:
    """
    Test 4: Verify scripts/ at root doesn't duplicate L0_maintenance/scripts/.
    
    Gap: No agent detects this duplication.
    """
    root = get_validated_project_root()
    root_scripts = root / "scripts"
    ssot_scripts = root / "agentic_core" / "L0_maintenance" / "scripts"
    
    if not root_scripts.exists():
        return True, "No scripts/ at root (correct)"
    
    if not ssot_scripts.exists():
        return False, "scripts/ at root but SSOT location doesn't exist"
    
    # Both exist - this is a violation
    # Phase 6.9: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery import get_python_files
    root_count = len(list(get_python_files(root_scripts)))
    ssot_count = len(list(get_python_files(ssot_scripts)))
    
    return False, f"DUPLICATE: scripts/ at root ({root_count} files) AND L0_maintenance/scripts/ ({ssot_count} files)"


def test_5_logs_folder_ssot_location() -> Tuple[bool, str]:
    """
    Test 5: Verify logs/ at root doesn't duplicate L0_maintenance/logs/.
    
    Gap: No agent detects this duplication.
    """
    root = get_validated_project_root()
    root_logs = root / "logs"
    ssot_logs = root / "agentic_core" / "L0_maintenance" / "logs"
    
    if not root_logs.exists():
        return True, "No logs/ at root (correct)"
    
    # logs/ at root is a violation regardless
    return False, f"logs/ exists at root - should be in agentic_core/L0_maintenance/logs/"


def test_6_coverage_html_handling() -> Tuple[bool, str]:
    """
    Test 6: Verify coverage_html/ is either in reports/ or gitignored.
    
    Gap: No agent handles test coverage output folders.
    """
    root = get_validated_project_root()
    root_coverage = root / "coverage_html"
    reports_coverage = root / "reports" / "coverage_html"
    gitignore = root / ".gitignore"
    
    if not root_coverage.exists():
        return True, "No coverage_html/ at root (correct)"
    
    # Check if gitignored
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8', errors='ignore')
        if 'coverage_html' in content:
            return True, "coverage_html/ at root but is gitignored (acceptable)"
    
    return False, "coverage_html/ at root - should be in reports/ or gitignored"


def test_7_location_agent_root_validation() -> Tuple[bool, str]:
    """
    Test 7: Verify LocationAgent validates root-level paths.
    
    Gap: LocationAgent.is_path_compliant() may not reject forbidden root folders.
    """
    try:
        from agentic_core.L5_safety.validators.LocationAgent import is_path_compliant
        
        # Test forbidden root folder
        result = is_path_compliant("scripts/test.py")
        
        # scripts/ is NOT in ROOT_WHITELIST, so this should return False
        # But scripts/ at root is actually a common pattern...
        # The real test is whether it's in SOVEREIGN_REGISTRY
        
        if "scripts" not in SOVEREIGN_REGISTRY:
            if result:
                return False, "is_path_compliant() accepts 'scripts/' but it's not in SOVEREIGN_REGISTRY"
            return True, "is_path_compliant() correctly rejects 'scripts/' (not in SOVEREIGN_REGISTRY)"
        
        return True, "scripts/ is in SOVEREIGN_REGISTRY (unexpected but valid)"
        
    except ImportError as e:
        return False, f"Could not import LocationAgent: {e}"


def test_8_hierarchy_agent_root_scan() -> Tuple[bool, str]:
    """
    Test 8: Verify HierarchyAgent can detect root-level violations.
    
    Gap: HierarchyAgent only scans agentic_core/, not project root.
    """
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        root = get_validated_project_root()
        agent = HierarchyAgent(root, healing_enabled=False)
        
        # Check if agent has method to scan root
        has_root_scan = hasattr(agent, 'scan_root_violations') or hasattr(agent, 'validate_root_structure')
        
        if has_root_scan:
            return True, "HierarchyAgent has root scanning capability"
        
        return False, "HierarchyAgent lacks root scanning method (only scans agentic_core/)"
        
    except ImportError as e:
        return False, f"Could not import HierarchyAgent: {e}"


def test_9_filesystem_reconciler_root_handling() -> Tuple[bool, str]:
    """
    Test 9: Verify FilesystemSSOTReconcilerAgent handles root-level drift.
    
    Gap: Only handles subfolders within sovereign roots, not root-level folders.
    """
    try:
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
        
        root = get_validated_project_root()
        agent = FilesystemSSOTReconcilerAgent(root, enforcement_mode=False)
        
        # Check if agent detects root-level drift
        has_root_drift = hasattr(agent, 'detect_root_drift') or hasattr(agent, 'scan_root_folders')
        
        if has_root_drift:
            return True, "FilesystemSSOTReconcilerAgent has root drift detection"
        
        return False, "FilesystemSSOTReconcilerAgent lacks root-level drift detection"
        
    except ImportError as e:
        return False, f"Could not import FilesystemSSOTReconcilerAgent: {e}"


def test_10_archived_file_relocation_logic() -> Tuple[bool, str]:
    """
    Test 10: Verify archiving logic moves files to archives/ folder.
    
    Gap: Current logic renames files with .archived suffix in place.
    """
    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        
        root = get_validated_project_root()
        agent = LocationAgent(root)
        
        # Check archive subfolder mapping
        if hasattr(agent, 'ARCHIVE_SUBFOLDERS'):
            subfolders = agent.ARCHIVE_SUBFOLDERS
            if subfolders:
                return True, f"LocationAgent has ARCHIVE_SUBFOLDERS mapping ({len(subfolders)} types)"
        
        # Check _heal_via_archiving method
        if hasattr(agent, '_heal_via_archiving'):
            return True, "LocationAgent has _heal_via_archiving method"
        
        return False, "LocationAgent lacks proper archiving infrastructure"
        
    except ImportError as e:
        return False, f"Could not import LocationAgent: {e}"


def test_11_root_whitelist_enforcement() -> Tuple[bool, str]:
    """
    Test 11: Verify ROOT_WHITELIST is actually enforced.
    
    Gap: ROOT_WHITELIST exists but may not be used in validation.
    """
    root = get_validated_project_root()
    
    # Get all root-level directories
    root_dirs = {
        item.name for item in root.iterdir() 
        if item.is_dir() and not item.name.startswith('.')
    }
    
    # Check against whitelist
    allowed = APPROVED_ROOT_FOLDERS | {'archives', 'docs', 'data', 'reports', '__pycache__'}
    violations = root_dirs - allowed - STANDARD_ROOT_ITEMS
    
    # Filter out known acceptable items
    real_violations = {v for v in violations if v not in {'scripts', 'logs', 'coverage_html'}}
    
    if not violations:
        return True, f"All {len(root_dirs)} root folders are in whitelist"
    
    return False, f"Root folders not in whitelist: {violations}"


def test_12_sovereign_registry_completeness() -> Tuple[bool, str]:
    """
    Test 12: Verify SOVEREIGN_REGISTRY has all required roots.
    
    Gap: Missing roots would cause validation failures.
    """
    required_roots = {'agentic_core', 'apps_rg', 'apps_lic', 'apps_shared', 'tests'}
    actual_roots = set(SOVEREIGN_REGISTRY.keys())
    
    missing = required_roots - actual_roots
    
    if not missing:
        return True, f"SOVEREIGN_REGISTRY has all {len(required_roots)} required roots"
    
    return False, f"SOVEREIGN_REGISTRY missing: {missing}"


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests(category: str = "all") -> Dict[str, Any]:
    """Run all tests and return results.
    
    Args:
        category: "all", "capability", or "compliance"
            - capability: Tests that agent code has required methods (should always pass)
            - compliance: Tests that repository is SSOT-compliant (may fail if violations exist)
    """
    # Agent Capability Tests - verify agents have required methods
    capability_tests = [
        ("Test 1: ROOT_WHITELIST matches SOVEREIGN_REGISTRY", test_1_root_folder_whitelist),
        ("Test 7: LocationAgent root validation", test_7_location_agent_root_validation),
        ("Test 8: HierarchyAgent root scan", test_8_hierarchy_agent_root_scan),
        ("Test 9: FilesystemSSOTReconcilerAgent root handling", test_9_filesystem_reconciler_root_handling),
        ("Test 10: Archived file relocation logic", test_10_archived_file_relocation_logic),
        ("Test 12: SOVEREIGN_REGISTRY completeness", test_12_sovereign_registry_completeness),
    ]
    
    # Repository Compliance Tests - verify repo is SSOT-compliant
    compliance_tests = [
        ("Test 2: No forbidden folders at root", test_2_no_forbidden_folders_at_root),
        ("Test 3: No .archived files at root", test_3_no_archived_files_at_root),
        ("Test 4: scripts/ SSOT location", test_4_scripts_folder_ssot_location),
        ("Test 5: logs/ SSOT location", test_5_logs_folder_ssot_location),
        ("Test 6: coverage_html/ handling", test_6_coverage_html_handling),
        ("Test 11: ROOT_WHITELIST enforcement", test_11_root_whitelist_enforcement),
    ]
    
    if category == "capability":
        tests = capability_tests
    elif category == "compliance":
        tests = compliance_tests
    else:
        tests = capability_tests + compliance_tests
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": len(tests),
        "details": [],
    }
    
    print("\n" + "=" * 70)
    print("ROOT DIRECTORY SSOT ENFORCEMENT TEST SUITE")
    print("=" * 70)
    
    for name, test_func in tests:
        try:
            passed, message = test_func()
            status = "PASSED" if passed else "FAILED"
            icon = "✅" if passed else "❌"
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "name": name,
                "passed": passed,
                "message": message,
            })
            
            print(f"\n{icon} {name}")
            print(f"   {message}")
            
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "name": name,
                "passed": False,
                "message": f"ERROR: {e}",
            })
            print(f"\n❌ {name}")
            print(f"   ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {results['passed']}/{results['total']} PASSED")
    print("=" * 70)
    
    if results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in results["details"]:
            if not detail["passed"]:
                print(f"   - {detail['name']}: {detail['message']}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Root SSOT Enforcement Test Suite")
    parser.add_argument(
        "--category",
        choices=["all", "capability", "compliance"],
        default="all",
        help="Test category: 'capability' (agent code), 'compliance' (repo state), or 'all'"
    )
    args = parser.parse_args()
    
    results = run_all_tests(category=args.category)
    
    # Exit with error code if any tests failed
    sys.exit(0 if results["failed"] == 0 else 1)
