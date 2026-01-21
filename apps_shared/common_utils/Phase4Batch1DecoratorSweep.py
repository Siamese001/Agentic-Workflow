#!/usr/bin/env python3
"""
Phase 4 Batch 1: Result Normalization (The Decorator Sweep)

AST-aware script to add @standard_heal decorator to all heal_repository methods.

Usage:
    python scripts/phase4_batch1_decorator_sweep.py --dry-run
    python scripts/phase4_batch1_decorator_sweep.py --execute
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# Files to EXCLUDE from refactoring (sources of truth)
EXCLUDED_FILES = {
    "decorators.py",  # Contains the decorator definition
    "healer_mixin.py",  # Base implementation
    "infrastructure_mixin.py",  # Base implementation
    "SovereignBaseAgent.py",  # Root base class
    "conftest.py",  # Test fixtures
}

# Directories to exclude
EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    "archives",
    "void_violations",
    "node_modules",
    ".venv",
    "venv",
}

DECORATOR_IMPORT = "from agentic_core.L5_safety.validators.decorators import standard_heal"
DECORATOR_NAME = "@standard_heal"


def find_python_files(root: Path) -> list[Path]:
    """Find all Python files in agentic_core, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        # Skip excluded files
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def has_heal_repository_method(content: str) -> bool:
    """Check if file contains a heal_repository method definition."""
    return bool(re.search(r"def heal_repository\s*\(", content))


def already_has_decorator(content: str) -> bool:
    """Check if @standard_heal is already applied to heal_repository."""
    # Look for @standard_heal followed by def heal_repository
    pattern = r"@standard_heal\s*\n\s*def heal_repository\s*\("
    return bool(re.search(pattern, content))


def already_has_import(content: str) -> bool:
    """Check if the standard_heal import already exists."""
    return "from agentic_core.L5_safety.validators.decorators import standard_heal" in content


def find_import_insertion_point(content: str) -> int:
    """Find the best line to insert the import statement."""
    lines = content.split("\n")
    last_import_line = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    # Single-line docstring
                    continue
                in_docstring = True
                continue
        else:
            if docstring_char in stripped:
                in_docstring = False
            continue

        # Track imports
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_line = i

    return last_import_line


def add_decorator_to_heal_repository(content: str) -> tuple[str, int]:
    """Add @standard_heal decorator to heal_repository methods.

    Returns:
        Tuple of (modified_content, number_of_decorators_added)
    """
    lines = content.split("\n")
    modified_lines = []
    decorators_added = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line defines heal_repository
        if re.match(r"\s*def heal_repository\s*\(", line):
            # Check if previous line already has @standard_heal
            if i > 0 and "@standard_heal" in lines[i - 1]:
                # Already decorated
                modified_lines.append(line)
                i += 1
                continue

            # Get the indentation of the def line
            indent_match = re.match(r"^(\s*)", line)
            indent = indent_match.group(1) if indent_match else ""

            # Add the decorator with same indentation
            modified_lines.append(f"{indent}{DECORATOR_NAME}")
            decorators_added += 1

        modified_lines.append(line)
        i += 1

    return "\n".join(modified_lines), decorators_added


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file, adding decorator and import if needed.

    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "import_added": False,
        "decorators_added": 0,
        "skipped": False,
        "reason": None,
    }

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result

    # Skip if no heal_repository method
    if not has_heal_repository_method(content):
        result["skipped"] = True
        result["reason"] = "No heal_repository method"
        return result

    # Skip if already fully decorated
    if already_has_decorator(content):
        result["skipped"] = True
        result["reason"] = "Already has @standard_heal"
        return result

    modified_content = content

    # Add import if missing
    if not already_has_import(content):
        insert_line = find_import_insertion_point(content)
        lines = modified_content.split("\n")
        lines.insert(insert_line + 1, DECORATOR_IMPORT)
        modified_content = "\n".join(lines)
        result["import_added"] = True

    # Add decorator
    modified_content, decorators_added = add_decorator_to_heal_repository(modified_content)
    result["decorators_added"] = decorators_added

    # Write if not dry run and changes were made
    if not dry_run and (result["import_added"] or decorators_added > 0):
        try:
            file_path.write_text(modified_content, encoding="utf-8")
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 1: Add @standard_heal decorator")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files"
    )
    parser.add_argument("--execute", action="store_true", help="Actually modify files")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Please specify --dry-run or --execute")
        return

    dry_run = args.dry_run

    root = Path(__file__).parent.parent / "agentic_core"
    if not root.exists():
        print(f"Error: agentic_core directory not found at {root}")
        return

    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 1: Decorator Sweep")
    print(f"Scanning: {root}")
    print("-" * 60)

    files = find_python_files(root)
    print(f"Found {len(files)} Python files to analyze")

    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "decorators_added": 0,
        "files_skipped": 0,
    }

    modified_files = []

    for file_path in files:
        result = process_file(file_path, dry_run=dry_run)
        stats["files_processed"] += 1

        if result["skipped"]:
            stats["files_skipped"] += 1
            continue

        if result["import_added"] or result["decorators_added"] > 0:
            stats["files_modified"] += 1
            stats["imports_added"] += 1 if result["import_added"] else 0
            stats["decorators_added"] += result["decorators_added"]
            modified_files.append(result)

            # Show progress for modified files
            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            if result["import_added"]:
                print("    + Added import")
            if result["decorators_added"]:
                print(f"    + Added {result['decorators_added']} decorator(s)")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files modified:  {stats['files_modified']}")
    print(f"  Imports added:   {stats['imports_added']}")
    print(f"  Decorators added: {stats['decorators_added']}")
    print(f"  Files skipped:   {stats['files_skipped']}")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
