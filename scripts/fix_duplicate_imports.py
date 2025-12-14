#!/usr/bin/env python3
"""Fix duplicate imports in Python files."""

import logging
import os
import re
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_duplicate_imports(filepath: Any) -> None:
    """Remove duplicate imports from a file."""
    try:
        with OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
            CONTENT = f.read()

        # Find all imports
        IMPORTS = []
        LINES = content.split("\n")

        for i, line in enumerate(lines):
            STRIPPED = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append((i, stripped))

        # Find duplicates
        SEEN = set()
        DUPLICATES = []
        for idx, imp in imports:
            # Normalize import for comparison
            NORMALIZED = re.sub(r"\s+", " ", imp)
            if normalized in seen:
                duplicates.append(idx)
            else:
                seen.add(normalized)

        # Remove duplicate lines
        if duplicates:
            logger.info(f"{filepath}: Found {len(duplicates)} duplicate imports")
            for idx in reversed(duplicates):
                del lines[idx]

            with OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
                f.write("\n".join(lines))
            return True

        return False
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return False


def main() -> None:
    """Fix duplicate imports in all Python files."""
    COUNT = 0
    for root, dirs, files in os.walk("."):
        # Skip hidden and special directories
        DIRS[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            if file.endswith(".py") and not file.startswith("fix_"):
                FILEPATH = os.path.join(root, file)
                if fix_duplicate_imports(filepath):
                    COUNT += 1

    logger.info(f"Fixed duplicate imports in {count} files")


if __name__ == "__main__":
    main()
