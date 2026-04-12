#!/usr/bin/env python3
"""
Fix corrupted __init__.py files where config constants were inserted incorrectly.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def fix_init_file(file_path: Path) -> bool:
    """Fix a corrupted __init__.py file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow - acceptable exception handling
    except (UnicodeDecodeError, OSError):
        return False

    # Check if file has the corruption pattern
    if "from " in content and "=" in content and "Configuration constants" in content:
        lines = content.splitlines()

        # Find the corrupted import
        fixed_lines = []
        config_constants = []
        in_import = False
        import_start = None

        for i, line in enumerate(lines):
            if line.startswith("from ") and "(" in line and not line.endswith(")"):
                in_import = True
                import_start = i
                fixed_lines.append(line)
            elif in_import:
                if line.strip().startswith("=") and "Configuration constants" not in line:
                    # This is a config constant in wrong place
                    config_constants.append(line.strip())
                elif line.strip() == ")":
                    # End of import
                    fixed_lines.append(line)
                    in_import = False
                elif line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                    # Unexpected line in import
                    if "=" in line:
                        config_constants.append(line.strip())
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        # If we found config constants, fix the file
        if config_constants and import_start is not None:
            # Insert config constants at the beginning
            new_lines = []

            # Add docstring if present
            for line in fixed_lines[:import_start]:
                new_lines.append(line)

            # Add config constants
            new_lines.append("")
            new_lines.append("# Configuration constants")
            for const in config_constants:
                new_lines.append(const)
            new_lines.append("")

            # Add the rest
            for line in fixed_lines[import_start:]:
                new_lines.append(line)

            # Write fixed content
            file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            return True

    return False


def main() -> None:
    """Fix all corrupted __init__.py files."""
    print("Fixing corrupted __init__.py files...")

    init_files = list(REPO.rglob("__init__.py"))

    fixed_count = 0
    for init_file in init_files:
        if fix_init_file(init_file):
            print(f"  Fixed: {init_file.relative_to(REPO)}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} __init__.py files")


if __name__ == "__main__":
    main()
