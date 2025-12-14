import logging
#!/usr/bin/env python3
"""Automatically remove unused imports from Python files."""

import ast
import os
from typing import List, Set, Dict, Any, Optional, Tuple

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

def find_unused_imports(file_path: str) -> Tuple[Set[str], Dict[str, int]]:
    """Find unused imports in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=file_path)

        # Track all imports and their line numbers
        imports = {}
        import_lines = {}

        # Find all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = alias.name
                    import_lines[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports[name] = f"{node.module}.{alias.name}" if node.module else alias.name
                    import_lines[name] = node.lineno

logger = logging.getLogger(__name__)

        # Find all used names
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Handle attribute access like module.function
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        # Find unused imports (excluding special cases)
        unused = set()
        for imp in imports:
            if imp not in used_names and not imp.startswith('_'):
                # Skip some common special cases
                if imports[imp] not in ['__future__', 'typing', 'typing_extensions']:
                    unused.add(imp)

        return unused, import_lines

    except Exception as e:
        logger.info(f"Error analyzing {file_path}: {e}")
        return set(), {}

def remove_unused_imports(file_path: str, unused_imports: Set[str]) -> bool:
    """Remove unused imports from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        new_lines = []

        for i, line in enumerate(lines):
            should_remove = False
            line_stripped = line.strip()

            # Check if this line contains an unused import
            for unused in unused_imports:
                # Handle 'import x' or 'import x as y'
                if line_stripped.startswith(f'import {unused} ') or
                    line_stripped == f'import {unused}':
                    should_remove = True
                    modified = True
                    break
                # Handle 'from x import y' or 'from x import y as z'
                elif line_stripped.startswith('from ') and f' import {unused}' in line_stripped:
                    # Check if it's a single import on this line
                    if line_stripped.endswith(f' import {unused}') or
                        f' import {unused} as ' in line_stripped:
                        should_remove = True
                        modified = True
                        break
                    # Handle multi-line imports
                    elif line_stripped.endswith('('):
                        # Look ahead to find the closing parenthesis
                        j = i + 1
                        while j < len(lines) and ')' not in lines[j]:
                            j += 1
                        if j < len(lines):
                            # Check if unused import is in this multi-line block
                            block = ''.join(lines[i:j+1])
                            if f'\n    {unused}\n' in block or f'\n    {unused} as ' in block:
                                # Remove the specific line from the block
                                block_lines = block.split('\n')
                                new_block = []
                                for block_line in block_lines:
                                    if not (block_line.strip() == unused or
                                           block_line.strip().startswith(f'{unused} as ')):
                                        new_block.append(block_line)
                                # If block is now empty except for from/import, remove it all
                                if len(new_block) <= 2:
                                    should_remove = True
                                    modified = True
                                    # Skip ahead to consume the whole block
                                    for _ in range(j - i):
                                        lines[i+1] = ''
                                else:
                                    # Replace the block with the filtered version
                                    lines[i:j+1] = [new_block[0] +
                                        '\n'] +
                                            [l + '\n' for l in new_block[1:-1]] + [new_block[-1]]
                                    modified = True
                                    break

            if not should_remove:
                new_lines.append(line)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        return modified

    except Exception as e:
        logger.info(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix unused imports."""
    root_dir = "."
    python_files = get_python_files(root_dir)

    total_removed = 0
    files_modified = 0

    for file_path in python_files:
        if "canon_validator.py" in file_path:
            continue  # Skip the validator itself

        unused_imports, import_lines = find_unused_imports(file_path)

        if unused_imports:
            logger.info(f"\n{file_path}:")
            for imp in sorted(unused_imports):
                logger.info(f"  Line {import_lines.get(imp, '?')}: {imp}")

            if remove_unused_imports(file_path, unused_imports):
                files_modified += 1
                total_removed += len(unused_imports)

    logger.info(f"\nRemoved {total_removed} unused imports from {files_modified} files")

if __name__ == "__main__":
    main()
