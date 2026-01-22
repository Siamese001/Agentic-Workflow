#!/usr/bin/env python3
"""
Phase 4 Batch 3: Safe File I/O (The Encoding Fix)

Replace simple open() read patterns with safe_read_file().
This is a CONSERVATIVE refactor - only replaces simple, safe patterns.

CONSTRAINTS:
- Only replace simple patterns: with open(path, 'r', encoding='utf-8') as f: content = f.read()
- Do NOT replace JSON loads, binary reads, or complex patterns
- Do NOT modify file_utils.py itself

Usage:
    python scripts/phase4_batch3_safe_io.py --dry-run
    python scripts/phase4_batch3_safe_io.py --execute
"""


import argparse
import re

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "file_utils.py",
    "conftest.py",
    "phase4_batch1_decorator_sweep.py",
    "phase4_batch2_index_switch.py",
    "phase4_batch3_safe_io.py",
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

# Pattern to match simple read patterns
# Matches: with open(path, 'r', encoding='utf-8') as f:\n    content = f.read()
# or: with open(path, encoding='utf-8') as f:\n    content = f.read()
SIMPLE_READ_PATTERN = re.compile(
    r"with open\(([^,]+),\s*['\"]r['\"]\s*,\s*encoding\s*=\s*['\"]utf-8['\"]\)\s*as\s+(\w+):\s*\n\s+(\w+)\s*=\s*\2\.read\(\)",
    re.MULTILINE,
)

# Alternative pattern without 'r' mode (defaults to read)
SIMPLE_READ_PATTERN_ALT = re.compile(
    r"with open\(([^,]+),\s*encoding\s*=\s*['\"]utf-8['\"]\)\s*as\s+(\w+):\s*\n\s+(\w+)\s*=\s*\2\.read\(\)",
    re.MULTILINE,
)

SAFE_IO_IMPORT = "from agentic_core.utils.file_utils import safe_read_file"


def find_python_files(root: Path) -> list[Path]:
    """Find all Python files in agentic_core, excluding specified directories."""
    files = []
    for path in root.rglob("*.py"):
        if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def has_simple_read_pattern(content: str) -> bool:
    """Check if file contains simple read patterns."""
    return bool(SIMPLE_READ_PATTERN.search(content) or SIMPLE_READ_PATTERN_ALT.search(content))


def already_has_safe_io_import(content: str) -> bool:
    """Check if file already imports safe_read_file."""
    return "from agentic_core.utils.file_utils import safe_read_file" in content


def find_import_insertion_point(content: str) -> int:
    """Find the best line to insert the import statement."""
    lines = content.split("\n")
    last_import_line = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    continue
                in_docstring = True
                continue
        else:
            if docstring_char in stripped:
                in_docstring = False
            continue

        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_line = i

    return last_import_line


def replace_simple_reads(content: str) -> tuple[str, int]:
    """Replace simple read patterns with safe_read_file().

    Returns:
        Tuple of (modified_content, number_of_replacements)
    """
    replacements = 0

    def replacer(match):
        nonlocal replacements
        path_expr = match.group(1)
        content_var = match.group(3)
        replacements += 1
        return f"{content_var} = safe_read_file({path_expr})"

    modified = SIMPLE_READ_PATTERN.sub(replacer, content)
    modified = SIMPLE_READ_PATTERN_ALT.sub(replacer, modified)

    return modified, replacements


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.

    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "import_added": False,
        "replacements": 0,
        "skipped": False,
        "reason": None,
    }

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result

    if not has_simple_read_pattern(content):
        result["skipped"] = True
        result["reason"] = "No simple read pattern"
        return result

    modified_content = content

    # Replace patterns first to count replacements
    modified_content, replacements = replace_simple_reads(modified_content)
    result["replacements"] = replacements

    if replacements == 0:
        result["skipped"] = True
        result["reason"] = "No replaceable patterns"
        return result

    # Add import if missing and we made replacements
    if not already_has_safe_io_import(content):
        insert_line = find_import_insertion_point(modified_content)
        lines = modified_content.split("\n")
        lines.insert(insert_line + 1, SAFE_IO_IMPORT)
        modified_content = "\n".join(lines)
        result["import_added"] = True

    if not dry_run:
        try:
            file_path.write_text(modified_content, encoding="utf-8")
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 3: Safe File I/O")
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

    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 3: Safe File I/O")
    print(f"Scanning: {root}")
    print("-" * 60)

    files = find_python_files(root)
    print(f"Found {len(files)} Python files to analyze")

    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "imports_added": 0,
        "replacements": 0,
        "files_skipped": 0,
    }

    for file_path in files:
        result = process_file(file_path, dry_run=dry_run)
        stats["files_processed"] += 1

        if result["skipped"]:
            stats["files_skipped"] += 1
            continue

        if result["import_added"] or result["replacements"] > 0:
            stats["files_modified"] += 1
            stats["imports_added"] += 1 if result["import_added"] else 0
            stats["replacements"] += result["replacements"]

            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            if result["import_added"]:
                print("    + Added safe_read_file import")
            if result["replacements"]:
                print(f"    + Replaced {result['replacements']} read pattern(s)")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files modified:  {stats['files_modified']}")
    print(f"  Imports added:   {stats['imports_added']}")
    print(f"  Replacements:    {stats['replacements']}")
    print(f"  Files skipped:   {stats['files_skipped']}")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()