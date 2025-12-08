#!/usr/bin/env python3
"""
STUB CLEANUP SCRIPT
===================
Removes empty stub files and cleans up placeholder structures.
Preserves files with meaningful TODO/PLACEHOLDER content for tracking.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import re

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Folders to skip
SKIP_FOLDERS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '06_data'}

# Files to always keep (even if empty)
KEEP_FILES = {'__init__.py', 'conftest.py', 'setup.py', 'pyproject.toml'}


def is_empty_or_minimal(file_path: Path) -> bool:
    """Check if file is empty or has minimal stub content."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore').strip()
        
        # Empty
        if not content:
            return True
        
        # Just pass or ellipsis
        if content in ['pass', '...']:
            return True
        
        # Comment + pass
        if re.match(r'^#[^\n]*\n\s*pass\s*$', content):
            return True
        
        # Docstring + pass only
        if re.match(r'^"""[^"]*"""\s*\n?\s*pass\s*$', content, re.DOTALL):
            return True
        if re.match(r"^'''[^']*'''\s*\n?\s*pass\s*$", content, re.DOTALL):
            return True
        
        return False
    except:
        return False


def has_meaningful_placeholder(file_path: Path) -> bool:
    """Check if file has meaningful placeholder content worth keeping."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Has TODO with description
        if re.search(r'TODO[:\s]+\w+', content, re.IGNORECASE):
            return True
        
        # Has PLACEHOLDER with context
        if re.search(r'PLACEHOLDER[:\s]+\w+', content, re.IGNORECASE):
            return True
        
        # Has actual function/class definitions (even if incomplete)
        if re.search(r'def\s+\w+\([^)]*\):', content) and len(content) > 100:
            return True
        if re.search(r'class\s+\w+', content) and len(content) > 100:
            return True
        
        return False
    except:
        return False


def remove_empty_directories(start_path: Path) -> List[str]:
    """Remove empty directories recursively."""
    removed = []
    
    for dirpath, dirnames, filenames in os.walk(start_path, topdown=False):
        current = Path(dirpath)
        
        # Skip certain folders
        if any(skip in current.parts for skip in SKIP_FOLDERS):
            continue
        
        # Check if directory is empty (or only has __pycache__)
        contents = list(current.iterdir())
        real_contents = [c for c in contents if c.name not in ['__pycache__', '.DS_Store']]
        
        if not real_contents:
            try:
                shutil.rmtree(current)
                removed.append(str(current.relative_to(REPO_ROOT)))
            except:
                pass
    
    return removed


def cleanup_stubs() -> Dict:
    """Clean up stub files."""
    log = {
        "deleted_files": [],
        "kept_with_placeholders": [],
        "deleted_directories": [],
        "errors": [],
    }
    
    # First pass: delete empty/minimal files
    for py_file in list(REPO_ROOT.rglob("*.py")):
        # Skip certain folders
        if any(skip in py_file.parts for skip in SKIP_FOLDERS):
            continue
        
        # Skip files to always keep
        if py_file.name in KEEP_FILES:
            continue
        
        rel_path = str(py_file.relative_to(REPO_ROOT))
        
        if is_empty_or_minimal(py_file):
            # Check if it has meaningful placeholder content
            if has_meaningful_placeholder(py_file):
                log["kept_with_placeholders"].append(rel_path)
            else:
                try:
                    py_file.unlink()
                    log["deleted_files"].append(rel_path)
                except Exception as e:
                    log["errors"].append(f"{rel_path}: {e}")
    
    # Second pass: remove empty directories
    log["deleted_directories"] = remove_empty_directories(REPO_ROOT)
    
    return log


def main():
    print("=" * 70)
    print("STUB CLEANUP")
    print("=" * 70)
    
    # Run cleanup
    print("\n[STEP 1] Deleting empty/minimal stub files...")
    log = cleanup_stubs()
    
    print(f"  ✓ Deleted {len(log['deleted_files'])} empty files")
    print(f"  ✓ Kept {len(log['kept_with_placeholders'])} files with meaningful placeholders")
    print(f"  ✓ Removed {len(log['deleted_directories'])} empty directories")
    
    if log["errors"]:
        print(f"  ⚠ {len(log['errors'])} errors")
    
    # Show sample of deleted files
    print("\n## SAMPLE DELETED FILES (first 20)")
    for f in log["deleted_files"][:20]:
        print(f"  ✗ {f}")
    if len(log["deleted_files"]) > 20:
        print(f"  ... and {len(log['deleted_files']) - 20} more")
    
    # Show kept placeholders
    if log["kept_with_placeholders"]:
        print("\n## KEPT WITH PLACEHOLDERS")
        for f in log["kept_with_placeholders"][:10]:
            print(f"  → {f}")
    
    # Save log
    log_path = REPO_ROOT / "stub_cleanup_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"\nLog saved to: {log_path}")
    print("\nNext steps:")
    print("  1. git add -A")
    print("  2. git commit -m 'chore: remove empty stub files'")
    print("  3. Run stub_audit.py again to verify")


if __name__ == "__main__":
    main()
