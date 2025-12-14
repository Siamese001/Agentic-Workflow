import logging
#!/usr/bin/env python3
"""Automatically fix lines longer than 100 characters."""

import os
import re
from typing import List

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

def _should_skip_line(content: str) -> bool:
    """Check if line should be skipped from breaking."""
    return (content.strip().startswith('#') or
            '"""' in content or "'''" in content or
            content.strip().startswith('r"""') or
            content.strip().startswith("r'''"))

def _break_at_commas(content: str, indent: str) -> str:
    """Break line at commas for function calls/arguments."""
    parts = content.split(', ')
    if len(parts) <= 1:
        return None
    
    base_indent = len(indent)
    extra_indent = 4
    new_line = indent + parts[0] + ',\n'
    
    for part in parts[1:-1]:
        new_line += ' ' * (base_indent + extra_indent) + part + ',\n'
    
    new_line += ' ' * (base_indent + extra_indent) + parts[-1] + '\n'
    return new_line

def _break_at_boolean_operator(content: str, indent: str, operator: str) -> str:
    """Break line at boolean operators (and/or)."""
    parts = content.split(f' {operator} ')
    if len(parts) <= 1:
        return None
    
    base_indent = len(indent)
    extra_indent = 4
    new_line = indent + parts[0] + f' {operator} \n'
    
    for part in parts[1:]:
        new_line += ' ' * (base_indent + extra_indent) + part
    
    new_line += '\n'
    return new_line

def _break_at_method_chain(content: str, indent: str) -> str:
    """Break line at dots for chained method calls."""
    parts = content.split('.')
    if len(parts) <= 2:
        return None
    
    base_indent = len(indent)
    extra_indent = 4
    new_line = indent + parts[0] + '.\n'
    
    for part in parts[1:-1]:
        new_line += ' ' * (base_indent + extra_indent) + '.' + part + '.\n'
    
    new_line += ' ' * (base_indent + extra_indent) + '.' + parts[-1] + '\n'
    return new_line

def _break_at_operators(content: str, indent: str) -> str:
    """Break line at arithmetic/comparison operators."""
    operators = [' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ',
                 ' + ', ' - ', ' * ', ' / ', ' % ', ' // ']
    
    for op in operators:
        if op in content:
            parts = content.split(op)
            if len(parts) > 1:
                base_indent = len(indent)
                extra_indent = 4
                new_line = indent + parts[0] + op + '\n'
                new_line += ' ' * (base_indent + extra_indent) + op.join(parts[1:]) + '\n'
                return new_line
    
    return None

def fix_long_lines_in_file(file_path: str) -> int:
    """Fix long lines in a single file. Returns number of lines fixed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        fixed_count = 0
        new_lines = []

        for line in lines:
            stripped = line.rstrip()
            if len(stripped) <= 100:
                new_lines.append(line)
                continue

            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            content = line[len(indent):].rstrip()

            if _should_skip_line(content):
                new_lines.append(line)
                continue

            is_import = content.strip().startswith('import')
            result = None

            if not is_import and ', ' in content:
                result = _break_at_commas(content, indent)
            
            if not result and not is_import and ' and ' in content:
                result = _break_at_boolean_operator(content, indent, 'and')
            
            if not result and not is_import and ' or ' in content:
                result = _break_at_boolean_operator(content, indent, 'or')
            
            if not result and not is_import and '.' in content:
                result = _break_at_method_chain(content, indent)
            
            if not result and not is_import:
                result = _break_at_operators(content, indent)

            if result:
                new_lines.append(result)
                fixed_count += 1
                modified = True
            else:
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
