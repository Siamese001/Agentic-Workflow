#!/usr/bin/env python3
"""
Fix all corrupted Python files where config constants were inserted in imports.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Config constants that were incorrectly inserted
CONFIG_CONSTANTS = [
    "MAX_RETRIES = 3",
    "DEFAULT_SLEEP = 1.0",
    "THRESHOLD = 0.95",
    "BUFFER_SIZE = 8192",
    "BATCH_SIZE = 32",
    "MAX_DEPTH = 6",
    "MAX_FILES = 1000",
    "DEFAULT_TIMEOUT = 300  # 5 minutes",
]


def fix_python_file(file_path: Path) -> bool:
    """Fix a corrupted Python file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow - acceptable exception handling
    except (UnicodeDecodeError, OSError):
        return False

    original_content = content

    # Remove config constants from import statements
    lines = content.splitlines()
    fixed_lines = []
    extracted_constants = []
    in_multiline_import = False

    for line in lines:
        # Check if this is a config constant line
        if any(const in line for const in CONFIG_CONSTANTS):
            # If we're in an import, extract it
            if in_multiline_import or any("from " in l for l in fixed_lines[-5:] if "(" in l):
                extracted_constants.append(line.strip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

        # Track multiline imports
        if line.startswith("from ") and "(" in line and not line.endswith(")"):
            in_multiline_import = True
        elif in_multiline_import and line.strip() == ")":
            in_multiline_import = False

    # If we extracted constants, add them at the top
    if extracted_constants:
        # Find where to insert (after docstring/shebang)
        insert_pos = 0
        for i, line in enumerate(fixed_lines):
            if line.startswith('"""') and i > 0:
                # Find end of docstring
                for j in range(i + 1, len(fixed_lines)):
                    if '"""' in fixed_lines[j]:
                        insert_pos = j + 1
                        break
                break
            elif line.startswith("import ") or line.startswith("from "):
                insert_pos = i
                break

        # Insert config constants
        new_lines = (
            fixed_lines[:insert_pos]
            + ["", "# Configuration constants"]
            + extracted_constants
            + [""]
            + fixed_lines[insert_pos:]
        )

        content = "\n".join(new_lines) + "\n"

    # Write back if changed
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return True

    return False


def main() -> None:
    """Fix all corrupted Python files."""
    print("Fixing all corrupted Python files...")

    python_files = list(REPO.rglob("*.py"))

    # Skip certain directories
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".nox",
        "archives",
        ".backup",
    }

    fixed_count = 0
    for py_file in python_files:
        # Skip if in excluded directory
        if any(skip in py_file.parts for skip in skip_dirs):
            continue

        if fix_python_file(py_file):
            print(f"  Fixed: {py_file.relative_to(REPO)}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} Python files")


if __name__ == "__main__":
    main()
