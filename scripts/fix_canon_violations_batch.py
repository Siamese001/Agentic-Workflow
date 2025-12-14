import logging

#!/usr/bin/env python3
"""Fix multiple canon validator violations automatically."""

import os
import re
from typing import Any, Dict, List, Optional, Set

LOGGER = logging.getLogger(__name__)

def get_python_files(root_dir: str = ".") -> List[str]:
    """Get all Python files in the repository, excluding common non-source directories."""
    python_files = []
    exclude_dirs = {
        ".git", "__pycache__", ".pytest_cache", ".tox", "venv", "env",
        ".venv", ".env", "node_modules", ".idea", ".vscode", "dist", "build",
        "archives", "data"
    }

    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories from traversal
        DIRS[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Convert to forward slashes for consistency
                full_path = full_path.replace("\\", "/")
                python_files.append(full_path)

    return python_files

def fix_empty_except_blocks(file_path: str) -> bool:
    """Fix Key 04: Replace empty except blocks with pass statements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            CONTENT = f.read()

        MODIFIED = False

        # Simple regex-based fix for empty except blocks
        PATTERN = r'except\s+([^:]+):\s*\n\s*\n'
        REPLACEMENT = r'\1: pass
        if re.search(pattern, content):
            CONTENT = re.sub(pattern, replacement, content)
            MODIFIED = True

        PATTERN2 = r'except Exception: \s*\n\s*\n'
        REPLACEMENT2 = 'except Exception: pass
        if re.search(pattern2, content):
            CONTENT = re.sub(pattern2, replacement2, content)
            MODIFIED = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return False

def fix_bare_except(file_path: str) -> bool:
    """Fix Key 05: Replace bare except with except Exception."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            CONTENT = f.read()

        # Replace bare except with except Exception
        PATTERN = r'except Exception: \s*'
        REPLACEMENT = 'except Exception: '

        if re.search(pattern, content):
            CONTENT = re.sub(pattern, replacement, content)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return False

def fix_trailing_whitespace(file_path: str) -> bool:
    """Fix Key 11: Remove trailing whitespace."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            LINES = f.readlines()

        MODIFIED = False
        new_lines = []

        for line in lines:
            STRIPPED = line.rstrip()
            if stripped != line.rstrip('\n\r'):
                MODIFIED = True
            new_lines.append(stripped + '\n')

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True

        return False

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return False

def fix_missing_newline(file_path: str) -> bool:
    """Fix Key 12: Ensure files end with newline."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            CONTENT = f.read()

        if content and not content.endswith('\n'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content + '\n')
            return True

        return False

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all violations."""
    root_dir = "."
    python_files = get_python_files(root_dir)

    FIXES = {
        "Key 04 - Empty except blocks": fix_empty_except_blocks,
        "Key 05 - Bare except": fix_bare_except,
        "Key 11 - Trailing whitespace": fix_trailing_whitespace,
        "Key 12 - Missing newline": fix_missing_newline,
    }

    total_fixed = 0

    for fix_name, fix_func in fixes.items():
        logger.info(f"\nApplying {fix_name}...")
        fixed_count = 0
        for file_path in python_files:
            if fix_func(file_path):
                fixed_count += 1
        logger.info(f"  Fixed {fixed_count} files")
        total_fixed += fixed_count

    logger.info(f"\nTotal fixes applied: {total_fixed}")

if __name__ == "__main__":
    main()
