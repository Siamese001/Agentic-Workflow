#!/usr/bin/env python3
"""
Script to comment out all imports from archives/ in canonical files.
This protects the immutable archives from being loaded during validation.
import logging

LOGGER = logging.getLogger(__name__)

"""

import re
from pathlib import Path


def comment_archive_imports() -> None:
    """Find and comment out all imports from archives/ in canonical files."""
    ROOT = Path(__file__).parent.parent
    canonical_dirs = {
        'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared',
        'schemas', 'prompt_governance', 'observability', 'config',
        'tests', 'scripts'
    }

    # Pattern to match import statements from archives
    import_pattern = re.compile(
        r'^\s*(from\s+archives\.|import\s+archives\.)(.+)$')

    processed_files = 0
    commented_imports = 0

    # Walk through all Python files in canonical directories
    for py_file in root.rglob("*.py"):
        # Skip files in archives/ directory
        if "archives" in py_file.parts:
            continue

        # Only process files in canonical directories
        if not any(part in canonical_dirs for part in py_file.parts):
            continue

        # Debug: Print file being checked
        rel_path = py_file.relative_to(root)
        logger.info(f"Checking: {rel_path}")

        # Read file content
        try:
            CONTENT = py_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.info(f"Error reading {py_file}: {e}")
            continue

        # Check if file has archive imports
        if 'archives.' not in content:
            continue

        logger.info(f"Found archives in: {rel_path}")

        LINES = content.splitlines()
        MODIFIED = False

        # Process each line
        for i, line in enumerate(lines):
            MATCH = import_pattern.match(line)
            if match:
                # Comment out the import and add deprecation notice
                LINES[I] = f"# {line}  # DEPRECATED: Archive import removed to protect archives f...
                commented_imports += 1
                MODIFIED = True

        # Write back if modified
        if modified:
            py_file.write_text("\n".join(lines) + "\n", encoding='utf-8')
            processed_files += 1
            logger.info(f"Processed: {py_file.relative_to(root)}")

    logger.info(f"\nSummary:")
    logger.info(f"  Files processed: {processed_files}")
    logger.info(f"  Imports commented: {commented_imports}")

if __name__ == "__main__":
    comment_archive_imports()

