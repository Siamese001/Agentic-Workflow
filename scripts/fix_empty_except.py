#!/usr/bin/env python3
"""Fix empty except blocks in Python files."""

import os
from typing import Any
import glob
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_empty_except_blocks(directory: Any) -> None:
    """Fix empty except blocks by adding 'pass' or logging."""
    count = 0

    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        # Skip certain files
        if any(skip in filepath for skip in ['fix_empty_except.py', 'canon_validator.py']):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for empty except blocks
            empty_except_pattern = r'except\s*([^:]*):\s*\n\s*\n'
            matches = re.findall(empty_except_pattern, content)

            if matches:
                logger.info(f"{filepath}: Found {len(matches)} empty except blocks")

                # Fix empty except blocks
                # Add 'pass' statement to empty except blocks
                content = re.sub(
                    r'(except\s*[^:]*:\s*\n)\s*\n',
                    r'\1    pass\n\n',
                    content
                )

                # Also fix single-line empty except
                content = re.sub(
                    r'(except\s*[^:]*:\s*\n)\s*$',
                    r'\1    pass\n',
                    content,
                    flags=re.MULTILINE
                )

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Fixed empty except blocks in {count} files")

if __name__ == "__main__":
    fix_empty_except_blocks()
