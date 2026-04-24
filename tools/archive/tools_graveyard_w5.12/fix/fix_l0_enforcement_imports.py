#!/usr/bin/env python3
"""
Fix imports for L0 routing enforcement module.
Adds missing exports to __init__.py files so tests can import them.
"""

import ast
import pathlib


def get_exports_from_file(filepath):
    """Extract class and function names from a Python file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        exports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                exports.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):  # Only export public functions
                    exports.append(node.name)
        return exports
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"Error parsing {filepath}: {e}")
        return []


def update_init_file(init_path, all_exports):
    """Update __init__.py to include proper exports."""
    try:
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find the position after the existing imports
        lines = content.split("\n")

        # Look for the end of imports (before the first _emit_ call)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("_emit_") or line.strip().startswith("emit_"):
                insert_idx = i
                break

        # Create export statements
        export_lines = []
        for filepath, exports in all_exports.items():
            for export in sorted(exports):
                export_lines.append(f"from .{filepath.stem} import {export}")

        # Insert the new imports
        if export_lines:
            lines.insert(insert_idx, "")
            for line in reversed(export_lines):
                lines.insert(insert_idx, line)

        # Write back
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"Updated {init_path} with {len(export_lines)} exports")
        return True
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"Error updating {init_path}: {e}")
        return False


def main():
    """Main function to fix L0 routing enforcement imports."""
    enforcement_dir = pathlib.Path("agentic_core/L0_routing/enforcement")
    init_path = enforcement_dir / "__init__.py"

    if not init_path.exists():
        print(f"__init__.py not found at {init_path}")
        return

    # Get all exports from each module
    all_exports = {}
    for py_file in enforcement_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        exports = get_exports_from_file(py_file)
        if exports:
            all_exports[py_file] = exports
            print(f"Found {len(exports)} exports in {py_file.name}")

    # Update __init__.py
    if update_init_file(init_path, all_exports):
        print("Successfully updated L0 routing enforcement __init__.py")
    else:
        print("Failed to update __init__.py")


if __name__ == "__main__":
    main()
