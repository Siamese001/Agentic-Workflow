#!/usr/bin/env python3
"""
Fix broken import statements caused by regex replacement.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def fix_broken_imports():
    """Fix import statements with escaped dots."""
    print("🔧 Fixing broken import statements...")

    fixed_count = 0

    # Find all Python files
    for py_file in PROJECT_ROOT.rglob("*.py"):
        # Skip certain directories
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "node_modules", "archives"}
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Fix escaped dots in imports
            content = re.sub(
                r"from agentic_core\\\.L_CONTRACTS\\\.([^\s]+) import",
                r"from agentic_core.L_CONTRACTS.\1 import",
                content,
            )

            content = re.sub(
                r"import agentic_core\\\.L_CONTRACTS\\\.([^\s]+)",
                r"import agentic_core.L_CONTRACTS.\1",
                content,
            )

            content = re.sub(
                r"from agentic_core\\\.runtime\\\.([^\s]+) import",
                r"from agentic_core.runtime.\1 import",
                content,
            )

            content = re.sub(
                r"import agentic_core\\\.runtime\\\.([^\s]+)",
                r"import agentic_core.runtime.\1",
                content,
            )

            # Write back if changed
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                fixed_count += 1

                if fixed_count % 100 == 0:
                    print(f"  Fixed {fixed_count} files...")

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            print(f"  Error fixing {py_file}: {e}")

    print(f"✅ Fixed {fixed_count} files with broken imports")


def main():
    """Main entry point."""
    print("=" * 80)
    print("BROKEN IMPORTS FIXER")
    print("=" * 80)

    fix_broken_imports()

    print("\n🎉 BROKEN IMPORTS FIXED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
