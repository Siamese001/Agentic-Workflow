#!/usr/bin/env python3
"""
Process review_pending folder:
1. Extract unique large files with real code to proper locations
2. Archive the rest to 06_data/deprecated
"""

import shutil
import hashlib
from pathlib import Path
from datetime import datetime

REPO = Path('c:/Git/Agentic-Workflow')
REVIEW_PENDING = REPO / 'config/review_pending'
ARCHIVE_DIR = REPO / '06_data/deprecated/review_pending_archive'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def has_real_code(path: Path) -> bool:
    """Check if file has real implementation."""
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        if 'DO NOT implement logic here' in content:
            return False
        if 'AUTO-GENERATED ZERO-LOSS' in content and 'Phase 3 hydration' in content:
            return False
        # Check for substantial code
        lines = content.split('\n')
        code_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                code_lines += 1
        return code_lines > 20
    except Exception:
        return False


def main():
    print("=" * 80)
    print("PROCESSING review_pending FOLDER")
    print("=" * 80)
    
    # Find all Python files
    all_files = list(REVIEW_PENDING.rglob('*.py'))
    print(f"Total files: {len(all_files)}")
    
    # Categorize files
    large_real_code = []  # >5KB with real code
    small_or_stub = []    # <5KB or stubs
    
    seen_hashes = {}  # hash -> first file path
    
    for f in all_files:
        if '__pycache__' in str(f):
            continue
        
        size = f.stat().st_size
        h = get_file_hash(f)
        
        # Skip exact duplicates
        if h in seen_hashes:
            small_or_stub.append(f)
            continue
        seen_hashes[h] = f
        
        if size > 5000 and has_real_code(f):
            large_real_code.append((f, size))
        else:
            small_or_stub.append(f)
    
    print(f"\nLarge files with real code: {len(large_real_code)}")
    print(f"Small/stub files: {len(small_or_stub)}")
    
    # Show large files
    print("\n" + "-" * 80)
    print("LARGE FILES WITH REAL CODE (to be preserved):")
    print("-" * 80)
    
    for f, size in sorted(large_real_code, key=lambda x: -x[1])[:20]:
        rel = f.relative_to(REVIEW_PENDING)
        print(f"  {size:>8} bytes: {rel}")
    
    if len(large_real_code) > 20:
        print(f"  ... and {len(large_real_code) - 20} more")
    
    # Find the largest unique file (likely the main Resume Engine)
    if large_real_code:
        largest = max(large_real_code, key=lambda x: x[1])
        print(f"\n>>> LARGEST FILE: {largest[0].name} ({largest[1]} bytes)")
        
        # Copy to apps_rg as resume_generation_engine.py
        dest = REPO / '09_apps/apps_rg/resume_generation_engine.py'
        if not dest.exists():
            print(f"    Copying to: {dest.relative_to(REPO)}")
            shutil.copy2(largest[0], dest)
            print("    ✓ Copied")
        else:
            print(f"    Already exists: {dest.relative_to(REPO)}")
    
    # Create archive directory
    archive_path = ARCHIVE_DIR / TIMESTAMP
    archive_path.mkdir(parents=True, exist_ok=True)
    print(f"\nArchive directory: {archive_path.relative_to(REPO)}")
    
    # Move entire review_pending to archive
    print("\nMoving review_pending to archive...")
    
    # Count files to move
    files_moved = 0
    for f in REVIEW_PENDING.rglob('*'):
        if f.is_file() and '__pycache__' not in str(f):
            rel = f.relative_to(REVIEW_PENDING)
            dest = archive_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest))
            files_moved += 1
    
    print(f"  Moved {files_moved} files to archive")
    
    # Remove empty directories
    for d in sorted(REVIEW_PENDING.rglob('*'), reverse=True):
        if d.is_dir():
            try:
                d.rmdir()
            except OSError:
                ...
    
    # Remove review_pending if empty
    try:
        REVIEW_PENDING.rmdir()
        print("  Removed empty review_pending directory")
    except OSError:
        print("  review_pending directory not empty (some files remain)")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"  - Resume Generation Engine preserved in: 09_apps/apps_rg/resume_generation_engine.py")
    print(f"  - All files archived to: {archive_path.relative_to(REPO)}")
    print(f"  - review_pending folder deprecated")


if __name__ == '__main__':
    main()
