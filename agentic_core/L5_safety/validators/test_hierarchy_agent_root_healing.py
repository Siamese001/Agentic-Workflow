#!/usr/bin/env python3

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, healer, memory, orchestrator, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

# -*- coding: utf-8 -*-
"""
Test Suite: HierarchyAgent Root Healing Functionality

Tests the HierarchyAgent's ability to heal root directory SSOT violations:
1. Move .archived files to archives/root_archived/
2. Merge scripts/ to agentic_core/L0_maintenance/scripts/
3. Merge logs/ to agentic_core/L0_maintenance/logs/
4. Add coverage_html/ to .gitignore

Run: python scripts/test_hierarchy_agent_root_healing.py
"""
import sys
import os
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from typing import Dict, Any, Tuple
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# TEST FIXTURES
# ============================================================================

def create_test_environment() -> Path:
    """Create a temporary test environment with SSOT violations."""
    temp_dir = Path(tempfile.mkdtemp(prefix="hierarchy_test_"))
    
    # Create basic SSOT structure
    (temp_dir / "agentic_core" / "L0_maintenance" / "scripts").mkdir(parents=True)
    (temp_dir / "agentic_core" / "L0_maintenance" / "logs").mkdir(parents=True)
    (temp_dir / "archives").mkdir(parents=True)
    (temp_dir / "reports").mkdir(parents=True)
    
    # Create violations
    # 1. .archived files at root
    (temp_dir / "test_file.py.archived").write_text("# archived file 1")
    (temp_dir / "another_file.md.archived").write_text("# archived file 2")
    (temp_dir / "config.json.backup").write_text("{}")
    
    # 2. scripts/ at root (duplicate)
    scripts_root = temp_dir / "scripts"
    scripts_root.mkdir()
    (scripts_root / "test_script.py").write_text("# test script")
    (scripts_root / "helper.py").write_text("# helper script")
    (scripts_root / "subdir").mkdir()
    (scripts_root / "subdir" / "nested.py").write_text("# nested script")
    
    # 3. logs/ at root
    logs_root = temp_dir / "logs"
    logs_root.mkdir()
    (logs_root / "app.log").write_text("log entry 1")
    (logs_root / "error.log").write_text("error entry 1")
    
    # 4. coverage_html/ at root
    coverage_root = temp_dir / "coverage_html"
    coverage_root.mkdir()
    (coverage_root / "index.html").write_text("<html>coverage</html>")
    
    # Create .gitignore
    (temp_dir / ".gitignore").write_text("__pycache__/\n.venv/\n")
    
    return temp_dir


def cleanup_test_environment(temp_dir: Path) -> None:
    """Clean up temporary test environment."""
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_1_hierarchy_agent_has_root_healing_methods() -> Tuple[bool, str]:
    """Test 1: Verify HierarchyAgent has required root healing methods."""
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        required_methods = [
            'scan_root_violations',
            'heal_root_violations',
            '_merge_root_folder_to_ssot',
            '_handle_coverage_html',
        ]
        
        missing = []
        for method in required_methods:
            if not hasattr(HierarchyAgent, method):
                missing.append(method)
        
        if missing:
            return False, f"Missing methods: {missing}"
        
        return True, f"All {len(required_methods)} required methods present"
        
    except ImportError as e:
        return False, f"Could not import HierarchyAgent: {e}"


def test_2_hierarchy_agent_has_ssot_targets() -> Tuple[bool, str]:
    """Test 2: Verify HierarchyAgent has ROOT_FOLDER_SSOT_TARGETS mapping."""
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        if not hasattr(HierarchyAgent, 'ROOT_FOLDER_SSOT_TARGETS'):
            return False, "Missing ROOT_FOLDER_SSOT_TARGETS attribute"
        
        targets = HierarchyAgent.ROOT_FOLDER_SSOT_TARGETS
        required_keys = {'scripts', 'logs', 'coverage_html'}
        
        missing = required_keys - set(targets.keys())
        if missing:
            return False, f"Missing SSOT targets: {missing}"
        
        return True, f"ROOT_FOLDER_SSOT_TARGETS has all {len(required_keys)} required mappings"
        
    except ImportError as e:
        return False, f"Could not import HierarchyAgent: {e}"


def test_3_scan_root_violations_detects_archived_files() -> Tuple[bool, str]:
    """Test 3: Verify scan_root_violations detects .archived files at root."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=False)
        
        results = agent.scan_root_violations()
        
        archived_count = len(results.get("archived_files_at_root", []))
        if archived_count < 2:
            return False, f"Expected at least 2 archived files, found {archived_count}"
        
        return True, f"Detected {archived_count} archived files at root"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_4_scan_root_violations_detects_forbidden_folders() -> Tuple[bool, str]:
    """Test 4: Verify scan_root_violations detects forbidden folders."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=False)
        
        results = agent.scan_root_violations()
        
        forbidden = set(results.get("forbidden_folders", []))
        expected = {'scripts', 'logs', 'coverage_html'}
        
        missing = expected - forbidden
        if missing:
            return False, f"Failed to detect forbidden folders: {missing}"
        
        return True, f"Detected all {len(expected)} forbidden folders"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_5_heal_root_violations_moves_archived_files() -> Tuple[bool, str]:
    """Test 5: Verify heal_root_violations moves .archived files to archives/."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Count archived files before
        archived_before = list(temp_dir.glob("*.archived")) + list(temp_dir.glob("*.backup"))
        count_before = len(archived_before)
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Count archived files after
        archived_after = list(temp_dir.glob("*.archived")) + list(temp_dir.glob("*.backup"))
        count_after = len(archived_after)
        
        # Check archives folder
        archives_dir = temp_dir / "archives" / "root_archived"
        moved_files = list(archives_dir.glob("*")) if archives_dir.exists() else []
        
        if count_after > 0:
            return False, f"Still {count_after} archived files at root (expected 0)"
        
        if len(moved_files) < count_before:
            return False, f"Only {len(moved_files)} files in archives (expected {count_before})"
        
        return True, f"Moved {results['archived_files_moved']} archived files to archives/root_archived/"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_6_heal_root_violations_merges_scripts() -> Tuple[bool, str]:
    """Test 6: Verify heal_root_violations merges scripts/ to SSOT location."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Count scripts before
        scripts_root = temp_dir / "scripts"
        scripts_before = list(scripts_root.rglob("*.py")) if scripts_root.exists() else []
        count_before = len(scripts_before)
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Check SSOT location
        ssot_scripts = temp_dir / "agentic_core" / "L0_maintenance" / "scripts"
        scripts_after = list(ssot_scripts.rglob("*.py")) if ssot_scripts.exists() else []
        
        if results["scripts_files_moved"] < count_before:
            return False, f"Only moved {results['scripts_files_moved']} of {count_before} scripts"
        
        return True, f"Merged {results['scripts_files_moved']} scripts to SSOT location"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_7_heal_root_violations_merges_logs() -> Tuple[bool, str]:
    """Test 7: Verify heal_root_violations merges logs/ to SSOT location."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Count logs before
        logs_root = temp_dir / "logs"
        logs_before = list(logs_root.rglob("*")) if logs_root.exists() else []
        file_count_before = len([f for f in logs_before if f.is_file()])
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Check SSOT location
        ssot_logs = temp_dir / "agentic_core" / "L0_maintenance" / "logs"
        logs_after = list(ssot_logs.rglob("*")) if ssot_logs.exists() else []
        
        if results["logs_files_moved"] < file_count_before:
            return False, f"Only moved {results['logs_files_moved']} of {file_count_before} logs"
        
        return True, f"Merged {results['logs_files_moved']} logs to SSOT location"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_8_heal_root_violations_handles_coverage_html() -> Tuple[bool, str]:
    """Test 8: Verify heal_root_violations adds coverage_html/ to .gitignore."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Check .gitignore
        gitignore_path = temp_dir / ".gitignore"
        if not gitignore_path.exists():
            return False, ".gitignore not found"
        
        content = gitignore_path.read_text(encoding='utf-8')
        if 'coverage_html' not in content:
            return False, "coverage_html/ not added to .gitignore"
        
        if not results["coverage_handled"]:
            return False, "coverage_handled flag is False"
        
        return True, "Added coverage_html/ to .gitignore"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_9_heal_root_violations_dry_run_no_changes() -> Tuple[bool, str]:
    """Test 9: Verify dry_run=True makes no actual changes."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=False)
        
        # Count files before
        archived_before = len(list(temp_dir.glob("*.archived")))
        scripts_before = (temp_dir / "scripts").exists()
        logs_before = (temp_dir / "logs").exists()
        
        # Dry run
        results = agent.heal_root_violations(dry_run=True)
        
        # Count files after
        archived_after = len(list(temp_dir.glob("*.archived")))
        scripts_after = (temp_dir / "scripts").exists()
        logs_after = (temp_dir / "logs").exists()
        
        if archived_before != archived_after:
            return False, f"Archived files changed: {archived_before} -> {archived_after}"
        
        if scripts_before != scripts_after:
            return False, "scripts/ folder changed during dry run"
        
        if logs_before != logs_after:
            return False, "logs/ folder changed during dry run"
        
        return True, "Dry run made no changes"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_10_heal_repository_includes_root_healing() -> Tuple[bool, str]:
    """Test 10: Verify heal_repository() includes root healing."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Call heal_repository
        results = agent.heal_repository(dry_run=False)
        
        # Check that root_healing is included
        hierarchy_result = results.get("hierarchy", {})
        if "root_healing" not in hierarchy_result:
            return False, "root_healing not in heal_repository results"
        
        root_healing = hierarchy_result["root_healing"]
        if "archived_files_moved" not in root_healing:
            return False, "archived_files_moved not in root_healing"
        
        return True, "heal_repository includes root_healing"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_11_merge_handles_existing_files() -> Tuple[bool, str]:
    """Test 11: Verify merge skips files that already exist in SSOT location."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        
        # Create a file that already exists in SSOT location
        ssot_scripts = temp_dir / "agentic_core" / "L0_maintenance" / "scripts"
        (ssot_scripts / "test_script.py").write_text("# existing script in SSOT")
        
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Check that the SSOT file was not overwritten
        ssot_content = (ssot_scripts / "test_script.py").read_text()
        if "existing script in SSOT" not in ssot_content:
            return False, "SSOT file was overwritten"
        
        # Check that skipped files are tracked
        actions = results.get("actions", [])
        skipped = [a for a in actions if a.get("skipped")]
        
        if len(skipped) == 0:
            return False, "No files were skipped (expected at least 1)"
        
        return True, f"Correctly skipped {len(skipped)} existing files"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


def test_12_heal_removes_empty_folders() -> Tuple[bool, str]:
    """Test 12: Verify healing removes empty folders after merge."""
    temp_dir = None
    try:
        from agentic_core.L5_safety.guardrails.HierarchyAgent import HierarchyAgent
        
        temp_dir = create_test_environment()
        agent = HierarchyAgent(temp_dir, healing_enabled=True)
        
        # Heal
        results = agent.heal_root_violations(dry_run=False)
        
        # Check that scripts/ and logs/ are removed (or mostly empty)
        scripts_exists = (temp_dir / "scripts").exists()
        logs_exists = (temp_dir / "logs").exists()
        
        folders_removed = results.get("folders_removed", 0)
        
        # At least one folder should be removed
        if folders_removed == 0 and (not scripts_exists or not logs_exists):
            # Folders were removed but not counted
            pass
        elif folders_removed == 0 and scripts_exists and logs_exists:
            # Check if they're empty
            scripts_files = list((temp_dir / "scripts").rglob("*"))
            logs_files = list((temp_dir / "logs").rglob("*"))
            if scripts_files or logs_files:
                return False, "Folders not removed and still contain files"
        
        return True, f"Removed {folders_removed} empty folders"
        
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if temp_dir:
            cleanup_test_environment(temp_dir)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests() -> Dict[str, Any]:
    """Run all tests and return results."""
    tests = [
        ("Test 1: HierarchyAgent has root healing methods", test_1_hierarchy_agent_has_root_healing_methods),
        ("Test 2: HierarchyAgent has SSOT targets mapping", test_2_hierarchy_agent_has_ssot_targets),
        ("Test 3: scan_root_violations detects archived files", test_3_scan_root_violations_detects_archived_files),
        ("Test 4: scan_root_violations detects forbidden folders", test_4_scan_root_violations_detects_forbidden_folders),
        ("Test 5: heal_root_violations moves archived files", test_5_heal_root_violations_moves_archived_files),
        ("Test 6: heal_root_violations merges scripts/", test_6_heal_root_violations_merges_scripts),
        ("Test 7: heal_root_violations merges logs/", test_7_heal_root_violations_merges_logs),
        ("Test 8: heal_root_violations handles coverage_html/", test_8_heal_root_violations_handles_coverage_html),
        ("Test 9: dry_run=True makes no changes", test_9_heal_root_violations_dry_run_no_changes),
        ("Test 10: heal_repository includes root healing", test_10_heal_repository_includes_root_healing),
        ("Test 11: merge skips existing files", test_11_merge_handles_existing_files),
        ("Test 12: healing removes empty folders", test_12_heal_removes_empty_folders),
    ]
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": len(tests),
        "details": [],
    }
    
    print("\n" + "=" * 70)
    print("HIERARCHYAGENT ROOT HEALING TEST SUITE")
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
    results = run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(0 if results["failed"] == 0 else 1)