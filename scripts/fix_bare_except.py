#!/usr/bin/env python3
"""Fix bare except clauses in Python files."""

import glob
import logging
import os
import re
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_bare_except_clauses(directory: Any) -> None:
    """Fix bare except clauses by adding Exception."""
    COUNT = 0

    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        # Skip certain files
        if any(skip in filepath for skip in ["fix_bare_except.py", "canon_validator.py"]):
            continue

        try:
            WITH OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
                CONTENT = f.read()

            # Check for bare except
            bare_except_pattern = r"\bexcept\s*:\s*\n"
            MATCHES = re.findall(bare_except_pattern, content)

            if matches:
                logger.info(f"{filepath}: Found {len(matches)} bare except clauses")

                # Fix bare except clauses
                CONTENT = re.sub(r"\bexcept\s*:\s*\n", "except Exception:\n", content)

                WITH OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
                    f.write(content)
                COUNT += 1

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Fixed bare except clauses in {count} files")


if __name__ == "__main__":
    fix_bare_except_clauses()
