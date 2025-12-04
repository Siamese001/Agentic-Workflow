#!/usr/bin/env python3
"""
Apps Domain Structure Fix Script

This script fixes the 09_apps domain by:
1. Creating apps_rg and apps_lic subdirectories
2. Moving files based on filename prefixes (rg_* vs lic_*)
3. Removing empty L1-L5 cognitive folders
4. Ensuring compliance with YAML governance rules
"""

from pathlib import Path
import shutil
import json
from typing import Dict, List

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()

# Apps domain configuration
APPS_DOMAIN = "09_apps"
APPS_ROOT = PROJECT_ROOT / APPS_DOMAIN

# Required subdirectories for apps domain
APPS_SUBDOMAINS = ["apps_rg", "apps_lic", "_unassigned_apps_unknown"]

# Forbidden L*/P* folders that should be removed
FORBIDDEN_PATTERNS = ["L1_cognition", "L2_execution", "L3_orchestration", "L4_memory", "L5_safety"]

# Protected patterns to preserve
PROTECTED_PATTERNS = ["__init__.py", "*.md"]

# Archive location
ARCHIVE_ROOT = PROJECT_ROOT / "06_data" / "phase1_legacy_folders" / "apps_structure_fix"


def find_all_files(root: Path) -> List[Path]:
    """Find all files in the apps domain."""
    files = []
    if not root.exists():
        return files
        
    for file_path in root.rglob("*"):
        if file_path.is_file():
            files.append(file_path)
    return files


def resolve_app_domain(file_path: Path) -> str:
    """
    Determine which apps subdomain a file belongs to based on filename.
    """
    filename = file_path.name.lower()
    
    if filename.startswith("rg_"):
        return "apps_rg"
    elif filename.startswith("lic_"):
        return "apps_lic"
    else:
        return "_unassigned_apps_unknown"


def create_apps_structure() -> None:
    """Create the required apps subdirectory structure."""
    print("[STRUCTURE] Creating apps domain subdirectories...")
    
    for subdomain in APPS_SUBDOMAINS:
        subdomain_path = APPS_ROOT / subdomain
        subdomain_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = subdomain_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"[CREATE] {init_file}")


def move_files_to_subdomains() -> Dict[str, int]:
    """Move files to appropriate apps subdomains based on filename prefixes."""
    stats = {
        "total_files_found": 0,
        "files_moved_rg": 0,
        "files_moved_lic": 0,
        "files_moved_unassigned": 0,
        "protected_files_skipped": 0
    }
    
    print("[MOVE] Analyzing files for apps subdomain routing...")
    
    all_files = find_all_files(APPS_ROOT)
    stats["total_files_found"] = len(all_files)
    
    for file_path in all_files:
        # Skip files already in correct subdomains
        relative_path = file_path.relative_to(APPS_ROOT)
        if len(relative_path.parts) > 0 and relative_path.parts[0] in APPS_SUBDOMAINS:
            continue
            
        # Skip protected files in root
        if file_path.name in PROTECTED_PATTERNS or file_path.suffix == ".md":
            stats["protected_files_skipped"] += 1
            print(f"[SKIP] Protected file: {relative_path}")
            continue
            
        # Determine target subdomain
        target_subdomain = resolve_app_domain(file_path)
        target_path = APPS_ROOT / target_subdomain / file_path.name
        
        # Move file
        if not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))
            print(f"[MOVE] {relative_path} -> {target_subdomain}/{file_path.name}")
            
            if target_subdomain == "apps_rg":
                stats["files_moved_rg"] += 1
            elif target_subdomain == "apps_lic":
                stats["files_moved_lic"] += 1
            else:
                stats["files_moved_unassigned"] += 1
    
    return stats


def remove_empty_forbidden_folders() -> int:
    """Remove empty L*/P* folders from apps domain."""
    removed_count = 0
    
    print("[CLEANUP] Removing empty forbidden folders...")
    
    for pattern in FORBIDDEN_PATTERNS:
        folder_path = APPS_ROOT / pattern
        if folder_path.exists() and folder_path.is_dir():
            if remove_empty_folder_recursive(folder_path):
                removed_count += 1
    
    return removed_count


def remove_empty_folder_recursive(folder: Path) -> bool:
    """Recursively remove empty folder."""
    if not folder.exists():
        return False
        
    removed_any = False
    
    # Walk the tree bottom-up to remove nested empties first
    try:
        for item in list(folder.iterdir()):
            if item.is_dir():
                if remove_empty_folder_recursive(item):
                    removed_any = True
    except OSError:
        pass
    
    # Remove this folder if it's now empty
    try:
        if folder.is_dir():
            items = list(folder.iterdir())
            if len(items) == 0:
                folder.rmdir()
                print(f"[REMOVE] Empty folder: {folder}")
                return True
            else:
                # Force remove if only contains empty subdirectories
                all_empty = True
                for item in items:
                    if item.is_file():
                        all_empty = False
                        break
                if all_empty:
                    # Remove all empty subdirectories first
                    for item in items:
                        if item.is_dir():
                            item.rmdir()
                            print(f"[REMOVE] Empty subfolder: {item}")
                    # Then remove the parent
                    folder.rmdir()
                    print(f"[REMOVE] Empty folder: {folder}")
                    return True
    except OSError as e:
        print(f"[WARN] Could not remove {folder}: {e}")
        
    return removed_any


def verify_final_structure() -> bool:
    """Verify the final apps domain structure is correct."""
    print("[VERIFY] Checking final apps domain structure...")
    
    # Check required subdomains exist
    for subdomain in APPS_SUBDOMAINS:
        subdomain_path = APPS_ROOT / subdomain
        if not subdomain_path.exists():
            print(f"[ERROR] Missing required subdomain: {subdomain}")
            return False
    
    # Check no forbidden folders remain
    for pattern in FORBIDDEN_PATTERNS:
        folder_path = APPS_ROOT / pattern
        if folder_path.exists():
            print(f"[ERROR] Forbidden folder still exists: {pattern}")
            return False
    
    print("[VERIFY] Apps domain structure is correct")
    return True


def main():
    """Main execution function."""
    print("=" * 60)
    print("APPS DOMAIN STRUCTURE FIX")
    print("=" * 60)
    
    # Create archive directory
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Create proper subdirectory structure
    create_apps_structure()
    
    # Step 2: Move files to appropriate subdomains
    move_stats = move_files_to_subdomains()
    
    # Step 3: Remove empty forbidden folders
    removed_folders = remove_empty_forbidden_folders()
    
    # Step 4: Verify final structure
    is_valid = verify_final_structure()
    
    # Generate report
    report = {
        "timestamp": "2025-12-04 apps_fix",
        "move_stats": move_stats,
        "folders_removed": removed_folders,
        "structure_valid": is_valid
    }
    
    report_path = PROJECT_ROOT / "06_data" / "phase1_indices" / "apps_structure_fix_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 60)
    print("APPS STRUCTURE FIX SUMMARY")
    print("=" * 60)
    for key, value in move_stats.items():
        print(f"{key}: {value}")
    print(f"Empty folders removed: {removed_folders}")
    print(f"Final structure valid: {is_valid}")
    print(f"Report saved to: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
