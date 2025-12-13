#!/usr/bin/env python3
"""
STUB CLEANUP SCRIPT
===================
Removes empty minimal files and cleans up stub structures.
Preserves files with meaningful PENDING content for tracking.
import logging

logger = logging.getLogger(__name__)

"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
import json

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
    except (ValueError, TypeError, KeyError):
        return False

def has_meaningful_content(file_path: Path) -> bool:
    """Check if file has meaningful content worth keeping."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Implementation pending
        if re.search(r'PENDING[:\s]+\w+', content, re.IGNORECASE):
            return True

        # Has meaningful implementation
        if re.search(r'IMPLEMENTATION[:\s]+\w+', content, re.IGNORECASE):
            return True

        # Has actual function/class definitions (even if incomplete)
        if re.search(r'def\s+\w+\([^)]*\):', content) and len(content) > 100:
            return True
        if re.search(r'class\s+\w+', content) and len(content) > 100:
            return True

        return False
    except (ValueError, TypeError, KeyError):
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
            except (ValueError, TypeError, KeyError):
                ...

    return removed

def cleanup_stubs() -> Dict:
    """Clean up minimal files."""
    log = {
        "deleted_files": [],
        "kept_with_content": [],
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
            # Check if it has meaningful content
            if has_meaningful_content(py_file):
                log["kept_with_content"].append(rel_path)
            else:
                try:
                    py_file.unlink()
                    log["deleted_files"].append(rel_path)
                except (ValueError, TypeError, KeyError) as e:
                    log["errors"].append(f"{rel_path}: {e}")

    log["deleted_directories"] = remove_empty_directories(REPO_ROOT)

    return log

def main() -> None:
    """Main entry point for stub cleanup."""

    # Run cleanup

    log = cleanup_stubs()

    if log["errors"]:
        logger.info(f"\nErrors encountered ({len(log['errors'])}):")
        for e in log["errors"][:5]:
            logger.info(f"  - {e}")
        if len(log["errors"]) > 5:
            logger.info(f"  ... and {len(log['errors']) - 5} more")

    # Show sample of deleted files
    logger.info(f"\nDeleted minimal files ({len(log['deleted_files'])}):")
    for f in log["deleted_files"][:20]:
        logger.info(f"  - {f}")

    if len(log["deleted_files"]) > 20:
        logger.info(f"  ... and {len(log['deleted_files']) - 20} more")

    # Show kept files
    if log["kept_with_content"]:
        logger.info(f"\nKept with content ({len(log['kept_with_content'])}):")
        for f in log["kept_with_content"][:10]:
            logger.info(f"  - {f}")
        if len(log["kept_with_content"]) > 10:
            logger.info(f"  ... and {len(log['kept_with_content']) - 10} more")

    # Save log
    log_path = REPO_ROOT / "stub_cleanup_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    main()
