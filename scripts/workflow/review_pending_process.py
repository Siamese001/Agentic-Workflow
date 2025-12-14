#!/usr/bin/env python3
"""
Process review_pending folder:
1. Extract unique large files with real code to proper locations
2. Archive the rest to 06_data/deprecated
import logging

logger = logging.getLogger(__name__)

"""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

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
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and n...
                code_lines += 1
        return code_lines > 20
    except (ValueError, TypeError, KeyError):
        return False

def _categorize_pending_file(f: Path,
    seen_hashes: Dict[str,
    Path]) -> Tuple[Optional[Tuple[Path,
    int]],
    Optional[Path]]:
    """Categorize a pending file as large real code or small/stub."""
    size = f.stat().st_size
    h = get_file_hash(f)

    # Skip exact duplicates
    if h in seen_hashes:
        return None, f

    seen_hashes[h] = f

    if size > 5000 and has_real_code(f):
        return (f, size), None
    else:
        return None, f

def main() -> None:
    """Main entry point for review pending process."""

    # Find all Python files
    all_files = list(REVIEW_PENDING.rglob('*.py'))

    # Categorize files
    large_real_code = []  # >5KB with real code
    small_or_stub = []    # <5KB or stubs

    seen_hashes = {}  # hash -> first file path

    for f in all_files:
        if '__pycache__' in str(f):
            continue

        large, small = _categorize_pending_file(f, seen_hashes)
        if large:
            large_real_code.append(large)
        if small:
            small_or_stub.append(small)

    # Show large files

    for f, size in sorted(large_real_code, key=lambda x: -x[1])[:20]:
        rel = f.relative_to(REVIEW_PENDING)
        logger.info(f"  - {rel} ({size} bytes)")

    if len(large_real_code) > 20:
        logger.info(f"  ... and {len(large_real_code) - 20} more")

    # Find the largest unique file (likely the main Resume Engine)
    if large_real_code:
        largest = max(large_real_code, key=lambda x: x[1])

        # Copy to apps_rg as resume_generation_engine.py
        dest = REPO / '09_apps/apps_rg/resume_generation_engine.py'
        if not dest.exists():
            logger.info(f"\nCopying largest file to {dest.relative_to(REPO)}")
            shutil.copy2(largest[0], dest)
        else:
            logger.info(f"\nDestination already exists: {dest.relative_to(REPO)}")

    # Create archive directory
    archive_path = ARCHIVE_DIR / TIMESTAMP
    archive_path.mkdir(parents=True, exist_ok=True)

    # Move entire review_pending to archive
    logger.info(f"\nMoving {len(list(REVIEW_PENDING.rglob('*')))} items to archive...")
    shutil.move(str(REVIEW_PENDING), str(archive_path / 'review_pending'))

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
                    pass

        try:
            REVIEW_PENDING.rmdir()
        except OSError:
            pass

if __name__ == '__main__':
    main()
