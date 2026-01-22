#!/usr/bin/env python3
"""
Fix __future__ import ordering across all Python files.

Moves `from __future__ import ...` to be the first line of the file,
preserving shebangs (#!) if present.
"""

from pathlib import Path


def fix_future_imports(file_path: Path) -> bool:
    """
    Fix __future__ import ordering in a single file.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Find all __future__ import lines
        future_lines = []
        future_indices = []

        for i, line in enumerate(lines):
            if "from __future__ import" in line and not line.strip().startswith("#"):
                future_lines.append(line)
                future_indices.append(i)

        if not future_lines:
            return False  # No __future__ imports

        # Check if already at the top (after shebang/encoding)
        first_future_idx = future_indices[0]

        # Find where __future__ should go
        insert_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#!"):  # Shebang
                insert_idx = i + 1
            elif stripped.startswith("# -*-") or stripped.startswith("# coding"):  # Encoding
                insert_idx = i + 1
            elif stripped.startswith("#") and i < 3:  # Comment at top
                insert_idx = i + 1
            else:
                break

        # Check if already correct
        if first_future_idx == insert_idx:
            return False

        # Remove future imports from current positions (reverse order to preserve indices)
        for idx in reversed(future_indices):
            lines.pop(idx)

        # Insert at correct position
        for i, future_line in enumerate(future_lines):
            lines.insert(insert_idx + i, future_line)

        # Write back
        new_content = "\n".join(lines)
        file_path.write_text(new_content, encoding="utf-8")

        return True

    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix __future__ imports across agentic_core."""
    print("\n" + "=" * 70)
    print("FIXING __future__ IMPORT ORDERING")
    print("=" * 70)

    root_dir = Path("agentic_core")
    files = list(root_dir.glob("**/*.py"))

    fixed_count = 0

    for file_path in files:
        # Skip backups and pycache
        if "__pycache__" in str(file_path) or ".sovereign_healing_backup" in str(file_path):
            continue

        if fix_future_imports(file_path):
            print(f"  ✅ Fixed: {file_path}")
            fixed_count += 1

    print("\n" + "=" * 70)
    print(f"Fixed {fixed_count} file(s)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
