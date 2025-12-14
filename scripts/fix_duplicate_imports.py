#!/usr/bin/env python3
"""Fix duplicate imports in Python files."""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_duplicate_imports(filepath):
    """Remove duplicate imports from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all imports
        imports = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append((i, stripped))

        # Find duplicates
        seen = set()
        duplicates = []
        for idx, imp in imports:
            # Normalize import for comparison
            normalized = re.sub(r'\s+', ' ', imp)
            if normalized in seen:
                duplicates.append(idx)
            else:
                seen.add(normalized)

        # Remove duplicate lines
        if duplicates:
            logger.info(f"{filepath}: Found {len(duplicates)} duplicate imports")
            for idx in reversed(duplicates):
                del lines[idx]

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True

        return False
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix duplicate imports in all Python files."""
    count = 0
    for root, dirs, files in os.walk('.'):
        # Skip hidden and special directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py') and not file.startswith('fix_'):
                filepath = os.path.join(root, file)
                if fix_duplicate_imports(filepath):
                    count += 1

    logger.info(f"Fixed duplicate imports in {count} files")

if __name__ == "__main__":
    main()
