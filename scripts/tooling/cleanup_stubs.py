#!/usr/bin/env python3
"""
STUB CLEANUP SCRIPT
===================
Removes empty minimal files and cleans up stub structures.
Preserves files with meaningful PENDING content for tracking.
import logging

LOGGER = logging.getLogger(__name__)

"""

import json
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Folders to skip
SKIP_FOLDERS = {'.git', '__pycache__',
    '.venv', 'venv', 'node_modules', '06_data'}

# Files to always keep (even if empty)
KEEP_FILES = {'__init__.py', 'conftest.py', 'setup.py', 'pyproject.toml'}


def is_empty_or_minimal(file_path: Path) -> bool:
    """Check if file is empty or has minimal stub content."""
    try:
        content = file_path.read_text(
            encoding='utf-8', errors='ignore').strip()

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
        pass
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
        pass
        return False


def remove_empty_directories(start_path: Path) -> List[str]:
    """Remove empty directories recursively."""
    REMOVED = []

    for dirpath, dirnames, filenames in os.walk(start_path, topdown=False):
        current = Path(dirpath)

        # Skip certain folders
        if any(skip in current.parts for skip in SKIP_FOLDERS):
            continue

        # Check if directory is empty (or only has __pycache__)
        contents = list(current.iterdir())
        real_contents = [c for c in contents if c.name not in [
            '__pycache__', '.DS_Store']]

        if not real_contents:
            try:
                shutil.rmtree(current)
                REMOVED.append(str(current.relative_to(REPO_ROOT)))
            except (ValueError, TypeError, KeyError):
                ...

    return REMOVED


def cleanup_stubs() -> Dict:
    """Clean up minimal files."""
    log = {
        # SQL query removed: [],
        "kept_with_content": [],
        # SQL query removed: [],
        "errors": [],
        "removed_files": [],
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
                    log["removed_files"].append(rel_path)
                except (ValueError, TypeError, KeyError) as e:
                    log["errors"].append(f"{rel_path}: {e}")

    log["removed_directories"] = remove_empty_directories(REPO_ROOT)

    return log

def main() -> None:
    """Main entry point for stub cleanup."""

    # Run cleanup

    LOG = cleanup_stubs()

    if LOG["errors"]:
        LOGGER.info(f"\nErrors encountered ({len(LOG['errors'])}):")
        for e in LOG["errors"][:5]:
            LOGGER.info(f"  - {e}")
        if len(LOG["errors"]) > 5:
            LOGGER.info(f"  ... and {len(LOG['errors']) - 5} more")

    # Show sample of deleted files
    LOGGER.info(f"\nRemoved files ({len(LOG['removed_files'])}):")
    for f in LOG['removed_files'][:20]:
        LOGGER.info(f"  - {f}")

    if len(LOG['removed_files']) > 20:
        LOGGER.info(f"  ... and {len(LOG['removed_files']) - 20} more")

    # Show removed directories
    LOGGER.info(f"\nRemoved directories ({len(LOG['removed_directories'])}):")
    for d in LOG['removed_directories'][:20]:
        LOGGER.info(f"  - {d}")

    if len(LOG['removed_directories']) > 20:
        LOGGER.info(f"  ... and {len(LOG['removed_directories']) - 20} more")


    # Show kept files
    if LOG["kept_with_content"]:
        LOGGER.info(f"\nKept with content ({len(LOG['kept_with_content'])}):")
        for f in LOG["kept_with_content"][:10]:
            LOGGER.info(f"  - {f}")
        if len(LOG["kept_with_content"]) > 10:
            LOGGER.info(f"  ... and {len(LOG['kept_with_content']) - 10} more")

    # Save log
    log_path = REPO_ROOT / "stub_cleanup_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(LOG, f, indent=2)

if __name__ == "__main__":
    main()