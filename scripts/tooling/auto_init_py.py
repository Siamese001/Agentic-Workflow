# scripts/auto_init_py.py
"""
Auto-initialize __init__.py files for Python packages.

This utility script automatically creates __init__.py files in directories
to ensure they are recognized as Python packages. It's useful for setting up
new modules or ensuring proper package structure in the Agentic-Workflow system.

Usage:
    python auto_init_py.py <path1> <path2> ...

The script will:
1. Create parent directories if they don't exist
2. Create __init__.py files in each parent directory
3. Skip existing __init__.py files

Author: Agentic-Workflow Team
Version: 1.0.0
import logging

logger = logging.getLogger(__name__)

"""

import pathlib
import sys
from typing import List


def create_init_files(paths: List[str]) -> int:
    """
    Create __init__.py files for the given paths.

    Args:
        paths: List of file/directory paths to process

    Returns:
        Number of __init__.py files created
    """
    created_count = 0

    for path_str in paths:
        path = pathlib.Path(path_str)
        parent = path.parent

        # Create parent directory if needed
        parent.mkdir(parents=True, exist_ok=True)

        # Create __init__.py if it doesn't exist
        init_file = parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Package initialization."""\n')
            created_count += 1
            logger.info(f"Created {init_file}")
        else:
            logger.info(f"Skipped existing {init_file}")

    return created_count


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        logger.info("Usage: python auto_init_py.py <path1> <path2> ...")
        sys.exit(1)

    created = create_init_files(sys.argv[1:])
    logger.info(f"\nCreated {created} __init__.py files")


if __name__ == "__main__":
    main()
