#!/usr/bin/env python3
"""Automatically add type hints to all functions missing them."""

import ast
import os
import re
from typing import List, Tuple


def add_type_hints_to_file(filepath: str) -> int:
    """Add type hints to all functions in a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        modified = False
        lines = content.split("\n")

        # Process nodes in reverse order to maintain line numbers
        for node in reversed(list(ast.walk(tree))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function already has type hints
                has_return_hint = node.returns is not None
                has_param_hints = all(arg.annotation is not None for arg in node.args.args)

                if not has_return_hint or not has_param_hints:
                    # Find the function definition line
                    func_line = node.lineno - 1

                    # Get the original line
                    original_line = lines[func_line]

                    # Build new function signature with type hints
                    params = []
                    for arg in node.args.args:
                        param = arg.arg
                        if arg.annotation is None:
                            param += ": Any"
                        else:
                            param += f": {ast.unparse(arg.annotation)}"
                        params.append(param)

                    # Add return type hint if missing
                    if node.returns is None:
                        return_type = " -> None"
                    else:
                        return_type = f" -> {ast.unparse(node.returns)}"

                    # Reconstruct the function signature
                    async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                    new_signature = (
                        f"{async_prefix}def {node.name}({', '.join(params)}){return_type}:"
                    )

                    # Replace the function signature
                    # Find the end of the signature (may span multiple lines)
                    end_line = func_line
                    paren_count = original_line.count("(") - original_line.count(")")
                    while paren_count > 0 and end_line + 1 < len(lines):
                        end_line += 1
                        paren_count += lines[end_line].count("(") - lines[end_line].count(")")

                    # Replace the multi-line signature
                    if end_line > func_line:
                        # Keep original indentation
                        indent = re.match(r"^(\s*)", original_line).group(1)
                        lines[func_line : end_line + 1] = [new_signature]
                    else:
                        lines[func_line] = new_signature

                    modified = True

        if modified:
            # Add Any import if needed
            if "Any" in "\n".join(lines) and "from typing import" not in content:
                # Find the first import line and add typing import after it
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        lines.insert(i + 1, "from typing import Any")
                        break
                else:
                    # No imports found, add at top
                    lines.insert(0, "from typing import Any")

            # Write back the modified content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return 1
        return 0
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return 0


def main() -> None:
    """Add type hints to all Python files."""
    fixed_count = 0

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                fixed_count += add_type_hints_to_file(filepath)

    logger.info(f"Added type hints to {fixed_count} files")


if __name__ == "__main__":
    main()
