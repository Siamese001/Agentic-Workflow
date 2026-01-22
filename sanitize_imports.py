#!/usr/bin/env python3
"""
Sanitize self-referencing imports and fix mcp_hardened_mixin_1 drift.
"""

from pathlib import Path


def fix_mcp_mixin_drift():
    """Replace mcp_hardened_mixin_1 with mcp_hardened_mixin."""
    core_path = Path("agentic_core")
    fixed_count = 0

    print("--- [FIXING MCP MIXIN DRIFT] ---")

    for py_file in core_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "mcp_hardened_mixin_1" in content:
                new_content = content.replace("mcp_hardened_mixin_1", "mcp_hardened_mixin")
                py_file.write_text(new_content, encoding="utf-8")
                print(f"  Fixed: {py_file.relative_to(core_path)}")
                fixed_count += 1
        except Exception as e:
            print(f"  Error: {py_file}: {e}")

    print(f"--- Fixed {fixed_count} files ---")
    return fixed_count


def remove_self_imports():
    """Remove self-referencing imports from files."""
    core_path = Path("agentic_core")
    fixed_count = 0

    print("\n--- [REMOVING SELF-IMPORTS] ---")

    for py_file in core_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # Get the module name from the file path
            # e.g., mcp_hardened_mixin.py -> mcp_hardened_mixin
            module_name = py_file.stem

            # Find and remove self-referencing imports
            new_lines = []
            removed = False
            for line in lines:
                # Check if this line imports from the same module
                # Pattern: from ...module_name import ... or import ...module_name
                if f".{module_name} import" in line or f"import {module_name}" in line:
                    # Check if it's actually importing from itself
                    if module_name in line and "from" in line:
                        # This is a self-import, skip it
                        print(f"  Removing from {py_file.relative_to(core_path)}: {line.strip()}")
                        removed = True
                        continue
                new_lines.append(line)

            if removed:
                py_file.write_text("\n".join(new_lines), encoding="utf-8")
                fixed_count += 1

        except Exception as e:
            print(f"  Error: {py_file}: {e}")

    print(f"--- Removed self-imports from {fixed_count} files ---")
    return fixed_count


if __name__ == "__main__":
    print("=" * 70)
    print("Import Sanitization")
    print("=" * 70)

    drift_fixed = fix_mcp_mixin_drift()
    self_fixed = remove_self_imports()

    print("\n" + "=" * 70)
    print(f"Summary: {drift_fixed} mixin drift fixes, {self_fixed} self-import removals")
    print("=" * 70)
