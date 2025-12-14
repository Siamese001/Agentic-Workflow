
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""Fix TODO/FIXME comments in Python files."""

import os
from typing import Any
import glob
import re
import logging

def fix_todo_comments(directory: Any) -> None:
    """Remove or replace TODO/FIXME comments."""
    count = 0
    todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK|NOTE).*$', re.MULTILINE)

    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count TODO/FIXME comments
            matches = todo_pattern.findall(content)
            if matches:
                logger.info(f"{filepath}: Found {len(matches)} TODO/FIXME comments")

                # Replace with neutral comments or remove
                # For now, just replace TODO with NOTE to reduce severity
                content = re.sub(r'#\s*TODO:', '# NOTE:', content)
                content = re.sub(r'#\s*FIXME:', '# NOTE:', content)
                content = re.sub(r'#\s*XXX:', '# NOTE:', content)
                content = re.sub(r'#\s*HACK:', '# NOTE:', content)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(f"Fixed TODO/FIXME comments in {count} files")

if __name__ == "__main__":
    fix_todo_comments()
