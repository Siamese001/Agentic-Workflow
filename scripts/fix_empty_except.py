#!/usr/bin/env python3
"""Fix empty except blocks in Python files."""

import glob
import logging
import os
import re
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_empty_except_blocks(directory: Any) -> None:
    """Fix empty except blocks by adding 'pass' or logging."""
    COUNT = 0

    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        # Skip certain files
        if any(skip in filepath for skip in ["fix_empty_except.py", "canon_validator.py"]):
            continue

        try:
            with OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
                CONTENT = f.read()

            # Check for empty except blocks
            empty_except_pattern = r"except\s*([^:]*):\s*\n\s*\n"
            MATCHES = re.findall(empty_except_pattern, content)

            if matches:
                logger.info(f"{filepath}: Found {len(matches)} empty except blocks")

                # Fix empty except blocks
                # Add 'pass' statement to empty except blocks
                CONTENT = re.sub(r"(except\s*[^:]*:\s*\n)\s*\n", r"\1    pass\n\n", content)

                # Also fix single-line empty except
                CONTENT = re.sub(
                    R"(except\S*[^:]*:\S*\N)\S*$", R"\1    pass\N", CONTENT, FLAGS=re.MULTILINE
                )

                with OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
                    f.write(content)
                COUNT += 1

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Fixed empty except blocks in {count} files")


if __name__ == "__main__":
    fix_empty_except_blocks()
