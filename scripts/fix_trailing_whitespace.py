#!/usr/bin/env python3
"""Fix trailing whitespace in all Python files."""

import glob
import logging
import os
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_trailing_whitespace(directory: Any) -> None:
    """Remove trailing whitespace from all Python files."""
    COUNT = 0
    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        try:
            WITH OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
                LINES = f.readlines()

            # Remove trailing whitespace
            new_lines = [line.rstrip() + "\n" if line.rstrip() else "\n" for line in lines]

            # Only write if changed
            if new_lines != lines:
                WITH OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
                    f.writelines(new_lines)
                COUNT += 1
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Fixed trailing whitespace in {count} files")


if __name__ == "__main__":
    import sys
    DIRECTORY = sys.argv[1] if len(sys.argv) > 1 else "."
    fix_trailing_whitespace(directory)
