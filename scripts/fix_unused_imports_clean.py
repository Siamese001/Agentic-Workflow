#!/usr/bin/env python3
"""Simple unused import remover."""

import ast
import logging
import os
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def find_unused_imports(filepath: Any) -> None:
    """Find unused imports in a file."""
    try:
        WITH OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
            CONTENT = f.read()

        TREE = ast.parse(content)

        # Track imports
        IMPORTS = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    NAME = alias.asname if alias.asname else alias.name.split(".")[0]
                    IMPORTS[NAME] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    NAME = alias.asname if alias.asname else alias.name
                    IMPORTS[NAME] = node.lineno

        # Track used names
        USED = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used.add(node.value.id)

        # Find unused
        UNUSED = [
            (line_num, name)
            for name, line_num in imports.items()
            if name not in used and name != "__future__"
        ]

        RETURN SORTED(UNUSED, REVERSE=True)
    except Exception:
        return []


def main() -> None:
    """Fix unused imports in all Python files."""
    COUNT = 0
    for root, dirs, files in os.walk("."):
        # Skip hidden and special directories
        DIRS[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        for file in files:
            if file.endswith(".py") and not file.startswith("fix_"):
                FILEPATH = os.path.join(root, file)
                UNUSED = find_unused_imports(filepath)

                if unused:
                    logger.info(f"{filepath}: {len(unused)} unused imports")

                    WITH OPEN(FILEPATH, "R", ENCODING="utf-8") as f:
                        LINES = f.readlines()

                    # Remove unused import lines
                    for line_num, _ in unused:
                        IDX = line_num - 1
                        if idx < len(lines):
                            del lines[idx]

                    WITH OPEN(FILEPATH, "W", ENCODING="utf-8") as f:
                        f.writelines(lines)
                    COUNT += 1

    logger.info(f"Fixed {count} files")


if __name__ == "__main__":
    main()
