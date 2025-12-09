#!/usr/bin/env python3
"""
FIX TEST STRUCTURE — YAML COMPLIANCE
=====================================
Fixes test structure to comply with unified_structure_subatomic_meta.yaml.
1. Removes L1-L5/P1-P4 folder mirroring in unit tests
2. Moves logic/ tests to appropriate categories
3. Flattens unit tests to domain-level only
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
import json

REPO_ROOT = Path(__file__).parent.parent.resolve()
TESTS_ROOT = REPO_ROOT / "tests"

# Forbidden L/P patterns to flatten
FORBIDDEN_PATTERNS = [
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_memory",
    "L5_safety",
    "P1_retrieve",
    "P2_inspect",
    "P3_aggregate",
    "P4_safety",
]

# Mapping for logic/ tests to proper categories
LOGIC_REMAP = {
    "test_cache_regression.py": ("unit", "runtime"),
    "test_planner_scoring_properties.py": ("unit", "agentic_core"),
    "test_safety_properties.py": ("golden", "safety"),
}


def flatten_unit_tests() -> List[str]:
    """
    Flatten unit tests by removing L/P folder nesting.
    Move all tests from unit/domain/L*/P*/ to unit/domain/
    """
    moved = []
    unit_dir = TESTS_ROOT / "unit"
    
    if not unit_dir.exists():
        return moved
    
    # Find all test files in L/P nested folders
    for domain_dir in unit_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        
        # Find all test files recursively
        for test_file in domain_dir.rglob("test_*.py"):
            rel_to_domain = test_file.relative_to(domain_dir)
            
            # Check if it's in an L/P folder
            has_lp = any(p in str(rel_to_domain) for p in FORBIDDEN_PATTERNS)
            
            if has_lp:
                # Move to domain root
                dest = domain_dir / test_file.name
                
                # Handle name conflicts
                if dest.exists() and dest != test_file:
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 1
                    while dest.exists():
                        dest = domain_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                
                if test_file != dest:
                    shutil.move(str(test_file), str(dest))
                    moved.append(f"{test_file.relative_to(TESTS_ROOT)} -> {dest.relative_to(TESTS_ROOT)}")
    
    return moved


def remove_empty_lp_dirs() -> List[str]:
    """Remove empty L/P directories after flattening."""
    removed = []
    unit_dir = TESTS_ROOT / "unit"
    
    if not unit_dir.exists():
        return removed
    
    # Walk bottom-up to remove empty dirs
    for domain_dir in unit_dir.iterdir():
        if not domain_dir.is_dir():
            continue
        
        for lp_pattern in FORBIDDEN_PATTERNS:
            for lp_dir in domain_dir.rglob(lp_pattern):
                if lp_dir.is_dir():
                    try:
                        # Remove if empty or only has __init__.py
                        contents = list(lp_dir.iterdir())
                        if not contents or all(f.name == "__init__.py" for f in contents):
                            shutil.rmtree(lp_dir)
                            removed.append(str(lp_dir.relative_to(TESTS_ROOT)))
                    except Exception as e:
                        print(f"  ⚠ Could not remove {lp_dir}: {e}")
    
    # Second pass: remove any remaining empty dirs
    for dirpath, dirnames, filenames in os.walk(unit_dir, topdown=False):
        current = Path(dirpath)
        if current == unit_dir:
            continue
        
        # Check if any part of path has L/P pattern
        rel_path = str(current.relative_to(unit_dir))
        has_lp = any(p in rel_path for p in FORBIDDEN_PATTERNS)
        
        if has_lp:
            contents = list(current.iterdir())
            if not contents or all(f.name in ["__init__.py", "__pycache__"] or f.name.startswith(".") for f in contents):
                try:
                    shutil.rmtree(current)
                    if str(current.relative_to(TESTS_ROOT)) not in removed:
                        removed.append(str(current.relative_to(TESTS_ROOT)))
                except:
                    ...
    
    return removed


def move_logic_tests() -> List[str]:
    """Move tests from logic/ to appropriate categories."""
    moved = []
    logic_dir = TESTS_ROOT / "logic"
    
    if not logic_dir.exists():
        return moved
    
    for test_file in logic_dir.glob("test_*.py"):
        if test_file.name in LOGIC_REMAP:
            category, subcategory = LOGIC_REMAP[test_file.name]
            dest_dir = TESTS_ROOT / category / subcategory
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest = dest_dir / test_file.name
            if not dest.exists():
                shutil.move(str(test_file), str(dest))
                moved.append(f"logic/{test_file.name} -> {category}/{subcategory}/{test_file.name}")
        else:
            # Default: move to unit/agentic_core
            dest_dir = TESTS_ROOT / "unit" / "agentic_core"
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest = dest_dir / test_file.name
            if not dest.exists():
                shutil.move(str(test_file), str(dest))
                moved.append(f"logic/{test_file.name} -> unit/agentic_core/{test_file.name}")
    
    # Remove logic/ if empty
    if logic_dir.exists():
        remaining = [f for f in logic_dir.iterdir() if f.name not in ["__init__.py", "__pycache__"]]
        if not remaining:
            shutil.rmtree(logic_dir)
            moved.append("Removed empty logic/ folder")
    
    return moved


def ensure_init_files() -> int:
    """Ensure all test directories have __init__.py."""
    created = 0
    
    for dirpath, dirnames, filenames in os.walk(TESTS_ROOT):
        current = Path(dirpath)
        init_file = current / "__init__.py"
        
        if not init_file.exists():
            init_file.write_text('"""Test package."""\n')
            created += 1
    
    return created


def main():
    print("=" * 70)
    print("FIX TEST STRUCTURE — YAML COMPLIANCE")
    print("=" * 70)
    
    log = {
        "flattened": [],
        "removed_dirs": [],
        "moved_logic": [],
        "init_files_created": 0,
    }
    
    # Step 1: Flatten unit tests
    print("\n[STEP 1] Flattening unit tests (removing L/P nesting)...")
    log["flattened"] = flatten_unit_tests()
    print(f"  ✓ Moved {len(log['flattened'])} test files")
    for item in log["flattened"][:5]:
        print(f"    {item}")
    if len(log["flattened"]) > 5:
        print(f"    ... and {len(log['flattened']) - 5} more")
    
    # Step 2: Remove empty L/P directories
    print("\n[STEP 2] Removing empty L/P directories...")
    log["removed_dirs"] = remove_empty_lp_dirs()
    print(f"  ✓ Removed {len(log['removed_dirs'])} directories")
    
    # Step 3: Move logic/ tests
    print("\n[STEP 3] Moving logic/ tests to proper categories...")
    log["moved_logic"] = move_logic_tests()
    print(f"  ✓ Moved {len(log['moved_logic'])} items")
    for item in log["moved_logic"]:
        print(f"    {item}")
    
    # Step 4: Ensure __init__.py files
    print("\n[STEP 4] Ensuring __init__.py files...")
    log["init_files_created"] = ensure_init_files()
    print(f"  ✓ Created {log['init_files_created']} __init__.py files")
    
    # Save log
    log_path = REPO_ROOT / "fix_test_structure_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    
    print("\n" + "=" * 70)
    print("TEST STRUCTURE FIX COMPLETE")
    print("=" * 70)
    print(f"\nLog saved to: {log_path}")
    print("\nRun test_structure_audit.py again to verify compliance.")


if __name__ == "__main__":
    main()
