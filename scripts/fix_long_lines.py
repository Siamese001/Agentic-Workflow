import logging
#!/usr/bin/env python3
"""Automatically fix lines longer than 100 characters."""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Any, Optional

logger = logging.getLogger(__name__)

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
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # Convert to forward slashes for consistency
                full_path = full_path.replace("\\", "/")
                python_files.append(full_path)

    return python_files

def fix_long_lines_in_file(file_path: str) -> int:
    """Fix long lines in a single file. Returns number of lines fixed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        fixed_count = 0
        new_lines = []

        for line in lines:
            # Skip comments and docstrings for now (they have different formatting rules)
            stripped = line.rstrip()
            if len(stripped) <= 100:
                new_lines.append(line)
                continue

            # Get indentation
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            content = line[len(indent):].rstrip()

            # Don't break certain patterns
            if (content.strip().startswith('#') or
                '"""' in content or "'''" in content or
                content.strip().startswith('r"""') or
                content.strip().startswith("r'''")):
                new_lines.append(line)
                continue

            # Strategy 1: Break at commas for function calls/arguments
            if ', ' in content and not content.strip().startswith('import'):
                parts = content.split(', ')
                if len(parts) > 1:
                    # First part stays on original line
                    new_line = indent + parts[0] + ',\n'
                    fixed_count += 1

                    # Subsequent parts get indented
                    base_indent = len(indent)
                    extra_indent = 4  # Standard Python continuation

                    for part in parts[1:-1]:
                        new_line += ' ' * (base_indent + extra_indent) + part + ',\n'

                    # Last part (without comma)
                    new_line += ' ' * (base_indent + extra_indent) + parts[-1] + '\n'
                    new_lines.append(new_line)
                    modified = True
                    continue

            # Strategy 2: Break at 'and' or 'or' for boolean expressions
            if ' and ' in content and not content.strip().startswith('import'):
                parts = content.split(' and ')
                if len(parts) > 1:
                    base_indent = len(indent)
                    extra_indent = 4

                    new_line = indent + parts[0] + ' and \n'
                    for part in parts[1:]:
                        new_line += ' ' * (base_indent + extra_indent) + part
                    new_line += '\n'
                    new_lines.append(new_line)
                    fixed_count += 1
                    modified = True
                    continue

            # Strategy 3: Break at 'or' for boolean expressions
            if ' or ' in content and not content.strip().startswith('import'):
                parts = content.split(' or ')
                if len(parts) > 1:
                    base_indent = len(indent)
                    extra_indent = 4

                    new_line = indent + parts[0] + ' or \n'
                    for part in parts[1:]:
                        new_line += ' ' * (base_indent + extra_indent) + part
                    new_line += '\n'
                    new_lines.append(new_line)
                    fixed_count += 1
                    modified = True
                    continue

            # Strategy 4: Break at '.' for chained method calls
            if '.' in content and not content.strip().startswith('import'):
                # Find good break points for method chaining
                parts = content.split('.')
                if len(parts) > 2:  # Only break if there are multiple chained calls
                    base_indent = len(indent)
                    extra_indent = 4

                    new_line = indent + parts[0] + '.\n'
                    for part in parts[1:-1]:
                        new_line += ' ' * (base_indent + extra_indent) + '.' + part + '.\n'
                    new_line += ' ' * (base_indent + extra_indent) + '.' + parts[-1] + '\n'
                    new_lines.append(new_line)
                    fixed_count += 1
                    modified = True
                    continue

            # Strategy 5: Break at operators for expressions
            operators = [' == ',
                ' != ',
                ' < ',
                ' > ',
                ' <= ',
                ' >= ',
                ' + ',
                ' - ',
                ' * ',
                ' / ',
                ' % ',
                ' // ']
            for op in operators:
                if op in content and not content.strip().startswith('import'):
                    parts = content.split(op)
                    if len(parts) > 1:
                        base_indent = len(indent)
                        extra_indent = 4

                        new_line = indent + parts[0] + op + '\n'
                        new_line += ' ' * (base_indent + extra_indent) + op.join(parts[1:]) + '\n'
                        new_lines.append(new_line)
                        fixed_count += 1
                        modified = True
                        break
            else:
                # If no strategy worked, keep original line
                new_lines.append(line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        return fixed_count

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return 0

def main():
    """Main function to fix long lines."""
    root_dir = "."
    python_files = get_python_files(root_dir)

    total_fixed = 0
    files_modified = 0

    for file_path in python_files:
        if "canon_validator.py" in file_path:
            continue  # Skip the validator itself

        fixed = fix_long_lines_in_file(file_path)
        if fixed > 0:
            files_modified += 1
            total_fixed += fixed

    logger.info(f"Fixed {total_fixed} long lines in {files_modified} files")

if __name__ == "__main__":
    main()
