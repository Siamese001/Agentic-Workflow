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
    except (ValueError, TypeError, KeyError):
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
    except (ValueError, TypeError, KeyError):
        return False

def main():

    # Find all Python files
    all_files = list(REVIEW_PENDING.rglob('*.py'))

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

    # Show large files

    for f, size in sorted(large_real_code, key=lambda x: -x[1])[:20]:
        rel = f.relative_to(REVIEW_PENDING)

    if len(large_real_code) > 20:

    # Find the largest unique file (likely the main Resume Engine)
    if large_real_code:
        largest = max(large_real_code, key=lambda x: x[1])

        # Copy to apps_rg as resume_generation_engine.py
        dest = REPO / '09_apps/apps_rg/resume_generation_engine.py'
        if not dest.exists():

            shutil.copy2(largest[0], dest)

        else:

    # Create archive directory
    archive_path = ARCHIVE_DIR / TIMESTAMP
    archive_path.mkdir(parents=True, exist_ok=True)

    # Move entire review_pending to archive

    # Count files to move
    files_moved = 0
    for f in REVIEW_PENDING.rglob('*'):
        if f.is_file() and '__pycache__' not in str(f):
            rel = f.relative_to(REVIEW_PENDING)
            dest = archive_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest))
            files_moved += 1

        for d in sorted(REVIEW_PENDING.rglob('*'), reverse=True):
        if d.is_dir():
            try:
                d.rmdir()
            except OSError:
                ...

        try:
        REVIEW_PENDING.rmdir()

    except OSError:

if __name__ == '__main__':
    main()
