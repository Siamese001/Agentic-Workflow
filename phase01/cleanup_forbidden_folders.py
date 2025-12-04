#!/usr/bin/env python3
"""
Phase 1 Cleanup Script - Remove forbidden L*/P* folders from operational_support domains

This script runs after Phase 1 to clean up empty cognitive folder structures
that violate domain governance rules (e.g., L1-L5 folders under 02_schemas).
"""

from pathlib import Path
import shutil
import json
from typing import Dict, List

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()

# Load governance config
SSOT_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

# Operational support domains that should NOT have L*/P* folders
OPERATIONAL_SUPPORT_DOMAINS = [
    "02_schemas", "03_runtime", "04_prompt_governance", 
    "05_config", "06_data", "07_observability", "08_scripts", "shared"
]

# Additional domains that need cleanup after Phase 1 structure creation
CLEANUP_DOMAINS = [
    "09_apps", "10_tests"  # These have correct subfolders but need L*/P* removal
]

# Protected patterns that should be archived, not deleted
PROTECTED_PATTERNS = ["__init__.py", "*.md"]

# Archive location for protected files
ARCHIVE_ROOT = PROJECT_ROOT / "06_data" / "phase1_legacy_folders" / "forbidden_folder_cleanup"


def load_yaml(path: Path) -> dict:
    """Load YAML safely."""
    import yaml
    if not path.exists():
        print(f"[WARN] YAML file not found: {path}")
        return {}
        
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    # Fix for literal block scalar (string) root
    if isinstance(data, str):
        try:
            data = yaml.safe_load(data)
        except Exception as e:
            print(f"[ERROR] Recursive YAML parse failed for {path}: {e}")
            return {}

    return data or {}


# Paths that Phase 1 must never touch (hard-coded safety)
HARD_PROTECTED_SUBPATHS = [
    Path("06_data/semantic_cache"),
]


def is_under_hard_protected(path: Path) -> bool:
    """Check if path is under any hard-coded protected subtree."""
    try:
        rel = path.relative_to(PROJECT_ROOT)
        for sub in HARD_PROTECTED_SUBPATHS:
            try:
                rel.relative_to(sub)
                return True
            except ValueError:
                continue
    except ValueError:
        pass
    return False


def is_forbidden_folder(folder_name: str) -> bool:
    """Check if folder name matches forbidden patterns L* or P*."""
    return folder_name.startswith(("L", "P")) and "_" in folder_name


def find_protected_files(folder: Path) -> List[Path]:
    """Find protected files in a folder that should be archived."""
    protected_files = []
    if not folder.exists():
        return protected_files
        
    for pattern in PROTECTED_PATTERNS:
        for file_path in folder.rglob(pattern):
            if file_path.is_file():
                protected_files.append(file_path)
    
    return protected_files


def archive_protected_files(files: List[Path], source_domain: str, dry_run: bool = False) -> None:
    """Move protected files to archive with preserved structure."""
    if not files:
        return
        
    print(f"[ARCHIVE] Moving {len(files)} protected files from {source_domain}")
    
    for file_path in files:
        # Check hard-protected paths first
        if is_under_hard_protected(file_path):
            print(f"[SKIP] Hard-protected file: {file_path}")
            continue
            
        # Create relative path from domain root
        try:
            rel_path = file_path.relative_to(PROJECT_ROOT / source_domain)
        except ValueError:
            rel_path = file_path.name
            
        # Create archive path
        archive_path = ARCHIVE_ROOT / source_domain / rel_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            print(f"[DRY-RUN] Would archive: {file_path} -> {archive_path}")
        else:
            # Move file to archive
            shutil.move(str(file_path), str(archive_path))
            print(f"[ARCHIVE] {file_path} -> {archive_path}")


def remove_empty_folders(folder: Path, dry_run: bool = False) -> bool:
    """Recursively remove empty folders."""
    if not folder.exists():
        return True
        
    # Check hard-protected paths first
    if is_under_hard_protected(folder):
        print(f"[SKIP] Hard-protected folder: {folder}")
        return False
        
    # Try to remove subdirectories first
    for subfolder in folder.iterdir():
        if subfolder.is_dir():
            remove_empty_folders(subfolder, dry_run)
    
    # Remove folder if it's empty
    try:
        if folder.is_dir() and len(list(folder.iterdir())) == 0:
            if dry_run:
                print(f"[DRY-RUN] Would remove empty folder: {folder}")
                return True
            else:
                folder.rmdir()
                print(f"[REMOVE] Empty folder: {folder}")
                return True
    except OSError as e:
        print(f"[WARN] Could not remove {folder}: {e}")
        return False
        
    return False


def cleanup_domain(domain_path: Path, dry_run: bool = False) -> Dict[str, int]:
    """Clean up forbidden folders in a specific domain."""
    stats = {
        "forbidden_folders_found": 0,
        "protected_files_archived": 0,
        "empty_folders_removed": 0
    }
    
    if not domain_path.exists():
        return stats
        
    print(f"\n[CLEANUP] Processing domain: {domain_path.name}")
    
    # Find all forbidden folders (L*, P*)
    forbidden_folders = []
    for item in domain_path.iterdir():
        if item.is_dir() and is_forbidden_folder(item.name):
            forbidden_folders.append(item)
    
    stats["forbidden_folders_found"] = len(forbidden_folders)
    
    for folder in forbidden_folders:
        print(f"[PROCESS] Forbidden folder: {folder}")
        
        # Find and archive protected files
        protected_files = find_protected_files(folder)
        if protected_files:
            archive_protected_files(protected_files, domain_path.name, dry_run)
            stats["protected_files_archived"] += len(protected_files)
        
        # Remove empty folder structure
        if remove_empty_folders(folder, dry_run):
            stats["empty_folders_removed"] += 1
    
    return stats


def main():
    """Main cleanup function."""
    import sys
    
    dry_run = "--dry-run" in sys.argv
    
    print("=" * 60)
    print(f"PHASE 1 CLEANUP - Remove Forbidden Folders ({'DRY RUN' if dry_run else 'EXECUTE'})")
    print("=" * 60)
    
    # Create archive directory (only in execute mode)
    if not dry_run:
        ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    
    total_stats = {
        "forbidden_folders_found": 0,
        "protected_files_archived": 0,
        "empty_folders_removed": 0
    }
    
    # Process each operational support domain
    all_domains = OPERATIONAL_SUPPORT_DOMAINS + CLEANUP_DOMAINS
    for domain in all_domains:
        domain_path = PROJECT_ROOT / domain
        stats = cleanup_domain(domain_path, dry_run)
        
        for key in total_stats:
            total_stats[key] += stats[key]
    
    # Generate cleanup report (only in execute mode)
    if not dry_run:
        report = {
            "timestamp": "2025-12-04 cleanup",
            "mode": "execute",
            "total_stats": total_stats,
            "domains_processed": all_domains
        }
        
        report_path = PROJECT_ROOT / "06_data" / "phase1_indices" / "cleanup_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
    
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    for key, value in total_stats.items():
        print(f"{key}: {value}")
    if dry_run:
        print("DRY RUN MODE - No files were actually moved or deleted")
        print("Run without --dry-run to execute the cleanup")
    print("=" * 60)


if __name__ == "__main__":
    main()
