#!/usr/bin/env python3
"""
Phase 4 Batch 1: Result Normalization (The Decorator Sweep) - V2

Apply @standard_heal decorator to heal_repository methods.

CRITICAL FIX: This version properly handles multi-line imports by:
1. Finding the LAST import statement that ends OUTSIDE of parentheses
2. Inserting new imports AFTER that line
3. Never inserting inside multi-line import blocks

Usage:
    python scripts/phase4_batch1_decorator_sweep_v2.py --dry-run
    python scripts/phase4_batch1_decorator_sweep_v2.py --execute
"""

import argparse
import re

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "decorators.py",
    "conftest.py",
    "healer_mixin.py",
    "infrastructure_mixin.py",
    "SovereignBaseAgent.py",
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

STANDARD_HEAL_IMPORT = "from agentic_core.L5_safety.validators.decorators import standard_heal"


def find_python_files(root: Path) -> list[Path]:
    """Find all Python files, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def has_heal_repository(content: str) -> bool:
    """Check if file contains a heal_repository method definition."""
    return bool(re.search(r"\n\s+def heal_repository\s*\(", content))


def already_has_standard_heal_import(content: str) -> bool:
    """Check if file already imports standard_heal."""
    return "from agentic_core.L5_safety.validators.decorators import standard_heal" in content


def already_has_decorator(content: str) -> bool:
    """Check if heal_repository already has @standard_heal decorator."""
    return bool(re.search(r"@standard_heal\s*\n\s+def heal_repository", content))


def find_safe_import_insertion_line(content: str) -> int:
    """Find the safe line number to insert a new import.

    This function properly handles multi-line imports by tracking parentheses depth.
    Returns the 0-indexed line number AFTER which to insert the new import.
    """
    lines = content.split("\n")
    last_safe_import_line = -1
    in_docstring = False
    docstring_char = None
    paren_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings (skip them)
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                # Check if docstring ends on same line
                if stripped.count(docstring_char) >= 2 and len(stripped) > 3:
                    continue
                in_docstring = True
                continue
        else:
            if docstring_char in stripped:
                in_docstring = False
            continue

        # Track parentheses depth for multi-line imports
        paren_depth += line.count("(") - line.count(")")

        # Only consider this a valid import line if we're at paren_depth 0 AFTER processing
        if stripped.startswith("import ") or stripped.startswith("from "):
            if paren_depth == 0:
                # This is a complete import statement (single line or end of multi-line)
                last_safe_import_line = i
        elif paren_depth == 0 and last_safe_import_line >= 0:
            # We've moved past imports, check if this closes a multi-line import
            if stripped == ")":
                last_safe_import_line = i

    # If we're still inside a multi-line import at the end, find the closing paren
    if paren_depth > 0:
        for i, line in enumerate(lines):
            if ")" in line:
                last_safe_import_line = i

    return last_safe_import_line


def insert_import_safely(content: str, import_line: str) -> str:
    """Insert an import statement at a safe location."""
    lines = content.split("\n")
    insert_after = find_safe_import_insertion_line(content)

    if insert_after < 0:
        # No imports found, insert after module docstring or at top
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
                and not stripped.startswith("'''")
            ):
                if stripped.startswith("from __future__"):
                    insert_after = i
                else:
                    insert_after = max(0, i - 1)
                    break

    # Insert the import
    lines.insert(insert_after + 1, import_line)
    return "\n".join(lines)


def add_decorator_to_heal_repository(content: str) -> tuple[str, int]:
    """Add @standard_heal decorator to heal_repository methods.

    Returns:
        Tuple of (modified_content, number_of_decorators_added)
    """
    # Pattern to find heal_repository method definitions without @standard_heal
    pattern = re.compile(r"(\n)([ \t]+)(def heal_repository\s*\()", re.MULTILINE)

    decorators_added = 0

    def replacer(match):
        nonlocal decorators_added
        newline = match.group(1)
        indent = match.group(2)
        method_def = match.group(3)

        # Check if there's already a @standard_heal decorator before this
        # by looking at the content before the match
        start = match.start()
        preceding = content[max(0, start - 100) : start]
        if "@standard_heal" in preceding.split("\n")[-1] if preceding else False:
            return match.group(0)

        decorators_added += 1
        return f"{newline}{indent}@standard_heal\n{indent}{method_def}"

    modified = pattern.sub(replacer, content)
    return modified, decorators_added


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.

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
    if not has_heal_repository(content):
        result["skipped"] = True
        result["reason"] = "No heal_repository method"
        return result

    # Skip if already has decorator
    if already_has_decorator(content):
        result["skipped"] = True
        result["reason"] = "Already has @standard_heal decorator"
        return result

    modified_content = content

    # Add import if missing
    if not already_has_standard_heal_import(content):
        modified_content = insert_import_safely(modified_content, STANDARD_HEAL_IMPORT)
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
    parser = argparse.ArgumentParser(description="Phase 4 Batch 1: Decorator Sweep V2")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
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

    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 1: Decorator Sweep V2")
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

            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            if result["import_added"]:
                print("    + Added standard_heal import")
            if result["decorators_added"]:
                print(f"    + Added {result['decorators_added']} @standard_heal decorator(s)")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed:   {stats['files_processed']}")
    print(f"  Files modified:    {stats['files_modified']}")
    print(f"  Imports added:     {stats['imports_added']}")
    print(f"  Decorators added:  {stats['decorators_added']}")
    print(f"  Files skipped:     {stats['files_skipped']}")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
