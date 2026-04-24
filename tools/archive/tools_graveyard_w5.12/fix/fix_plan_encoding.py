#!/usr/bin/env python3
"""
Plan Encoding Fix Tool
Fixes UTF-8 encoding errors in plan files that prevent validation.
"""

import sys
from pathlib import Path


def detect_encoding_issues(file_path: Path) -> bool:
    """Check if file has encoding issues."""
    try:
        with open(file_path, encoding="utf-8") as f:
            f.read()
        return False
    except UnicodeDecodeError:
        return True


def fix_encoding(file_path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """Fix encoding issues in a file."""
    if not detect_encoding_issues(file_path):
        return True, "No encoding issues found"

    if dry_run:
        return False, f"Would fix encoding issues in {file_path}"

    try:
        # Try multiple encodings
        encodings = ["utf-8", "latin-1", "cp1252", "charmap"]
        content = None
        encoding_used = None

        for enc in encodings:
            try:
                with open(file_path, encoding=enc) as f:
                    content = f.read()
                encoding_used = enc
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            return False, "Could not decode with any supported encoding"

        # Write back as UTF-8
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True, f"Fixed encoding (was {encoding_used}, now utf-8)"

    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return False, f"Error fixing encoding: {e}"


def find_encoding_issues(repo_root: Path) -> list[Path]:
    """Find all plan files with encoding issues."""
    plan_dirs = [
        repo_root / "docs" / "reports" / "plans",
        repo_root / ".windsurf" / "plans",
    ]

    problematic_files = []

    for plan_dir in plan_dirs:
        if not plan_dir.exists():
            continue

        for plan_path in plan_dir.rglob("*.md"):
            if plan_path.name == "README.md":
                continue

            if detect_encoding_issues(plan_path):
                problematic_files.append(plan_path)

    return problematic_files


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix encoding issues in plan files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.add_argument("--execute", action="store_true", help="Actually fix the encoding issues")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    problematic_files = find_encoding_issues(repo_root)

    print(f"Found {len(problematic_files)} files with encoding issues")

    if not problematic_files:
        print("No encoding issues found!")
        return

    success_count = 0
    error_count = 0

    for file_path in problematic_files:
        rel_path = str(file_path.relative_to(repo_root))
        success, message = fix_encoding(file_path, dry_run=args.dry_run)

        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        else:
            print(f"❌ {rel_path}: {message}")
            error_count += 1

    print("\nSummary:")
    print(f"  Total files: {len(problematic_files)}")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")

    if args.dry_run:
        print("\nRun with --execute to actually fix these files")


if __name__ == "__main__":
    main()
