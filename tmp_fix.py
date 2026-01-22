#!/usr/bin/env python3
"""
Atomic script to fix mcp_hardened_mixin_1 drift across the codebase.
Replaces all occurrences of 'mcp_hardened_mixin_1' with 'mcp_hardened_mixin'.
"""

import sys


def fix_mcp_imports(root_dir: str = "agentic_core"):
    """
    Replace mcp_hardened_mixin_1 with mcp_hardened_mixin in all Python files.

    Args:
        root_dir: Root directory to search (default: agentic_core)

    Returns:
        Tuple of (files_fixed, total_replacements)
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist")
        return 0, 0

    files_fixed = 0
    total_replacements = 0

    # Find all Python files
    python_files = list(root_path.rglob("*.py"))
    print(f"Scanning {len(python_files)} Python files in {root_dir}/...")

    for py_file in python_files:
        try:
            # Read file content
            content = py_file.read_text(encoding="utf-8", errors="ignore")

            # Count occurrences
            count = content.count("mcp_hardened_mixin_1")

            if count > 0:
                # Replace all occurrences
                new_content = content.replace("mcp_hardened_mixin_1", "mcp_hardened_mixin")

                # Write back to file
                py_file.write_text(new_content, encoding="utf-8")

                files_fixed += 1
                total_replacements += count
                print(f"  Fixed: {py_file.relative_to(root_path)} ({count} replacements)")

        except Exception as e:
            print(f"  Error processing {py_file}: {e}")

    return files_fixed, total_replacements


if __name__ == "__main__":
    print("=" * 70)
    print("MCP Hardened Mixin Drift Fix")
    print("=" * 70)

    files_fixed, total_replacements = fix_mcp_imports()

    print("=" * 70)
    print("Summary:")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Total replacements: {total_replacements}")
    print("=" * 70)

    if total_replacements > 0:
        print("✅ Mixin drift resolved successfully")
        sys.exit(0)
    else:
        print("ℹ️  No occurrences found (already fixed or none exist)")
        sys.exit(0)
