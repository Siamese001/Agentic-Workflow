
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""Automated fix for common syntax errors in Python files."""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple
import logging

def fix_docstring_in_signature(content: str) -> str:
    """Fix docstrings incorrectly placed inside function signatures."""
    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if we have a docstring after opening parenthesis
        if 'def ' in line and '(' in line and ')' not in line:
            # Look ahead for misplaced docstring
            j = i + 1
            while j < len(lines) and ')' not in lines[j]:
                if lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''"):
                    # Found misplaced docstring
                    # Move it before the function definition
                    docstring = lines[j]
                    del lines[j]
                    fixed_lines.append(docstring)
                    break
                j += 1
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)

def fix_missing_dataclass_import(content: str) -> Tuple[str, bool]:
    """Add missing dataclass import if @dataclass is used."""
    if '@dataclass' in content and 'from dataclasses import' not in content:
        # Find the import section
        lines = content.split('\n')
        import_idx = -1

        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i
            elif line.strip() == '' and import_idx >= 0:
                # Found end of import block
                break

        # Insert dataclass import
        if import_idx >= 0:
            lines.insert(import_idx + 1, 'from dataclasses import dataclass')
        else:
            lines.insert(0, 'from dataclasses import dataclass')

        return '\n'.join(lines), True

    return content, False

def fix_missing_enum_import(content: str) -> Tuple[str, bool]:
    """Add missing Enum import if Enum is used."""
    if 'Enum' in content and 'from enum import' not in content:
        # Find the import section
        lines = content.split('\n')
        import_idx = -1

        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i
            elif line.strip() == '' and import_idx >= 0:
                # Found end of import block
                break

        # Insert enum import
        if import_idx >= 0:
            lines.insert(import_idx + 1, 'from enum import Enum')
        else:
            lines.insert(0, 'from enum import Enum')

        return '\n'.join(lines), True

    return content, False

def fix_indentation_errors(content: str) -> str:
    """Fix common indentation errors."""
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Fix lines that start with docstring but have wrong indentation
        if line.strip().startswith('"""') and not line.startswith('    """') and not line.startswith('"""'):
            # Check if this is a class/method docstring
            if fixed_lines and (fixed_lines[-1].strip().endswith(':') or
                              (fixed_lines[-1].startswith('class ') or
                               fixed_lines[-1].startswith('def ') or
                               fixed_lines[-1].startswith('@'))):
                fixed_lines.append('    ' + line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def has_syntax_errors(file_path: Path) -> bool:
    """Check if a Python file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return False
    except (SyntaxError, IndentationError):
        return True

def fix_file(file_path: Path) -> bool:
    """Attempt to fix syntax errors in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        changed = False

        # Apply fixes
        content = fix_docstring_in_signature(content)
        if content != original_content:
            changed = True

        content, dataclass_added = fix_missing_dataclass_import(content)
        if dataclass_added:
            changed = True

        content, enum_added = fix_missing_enum_import(content)
        if enum_added:
            changed = True

        content = fix_indentation_errors(content)
        if content != original_content:
            changed = True

        # Write back if changed
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Fixed: {file_path}")
            return True

        return False

    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in runtime/ and tests/ directories."""
    base_dir = Path('.')
    fixed_count = 0

    # Find all Python files
    py_files = list(base_dir.glob('runtime/**/*.py')) + list(base_dir.glob('tests/**/*.py'))

    logger.info(f"Found {len(py_files)} Python files")

    for file_path in py_files:
        if has_syntax_errors(file_path):
            if fix_file(file_path):
                fixed_count += 1

    logger.info(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
