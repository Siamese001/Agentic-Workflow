#!/usr/bin/env python3
"""
Phase 4 Batch 4: Base Class Cleanup (The MRO Fix)

Remove redundant mixin inheritance from classes that inherit from SovereignBaseAgent.
Since SovereignBaseAgent now includes InfrastructureMixin (which has HealerMixin,
MCPHardenedMixin, SubatomicTestingMixin), these mixins are redundant when also
inheriting from SovereignBaseAgent.

CONSTRAINTS:
- Only remove HealerMixin, MCPHardenedMixin, SubatomicTestingMixin IF SovereignBaseAgent is present
- Preserve other mixins
- Ensure super().__init__() is still called

Usage:
    python scripts/phase4_batch4_mro_cleanup.py --dry-run
    python scripts/phase4_batch4_mro_cleanup.py --execute
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Files to EXCLUDE from refactoring
EXCLUDED_FILES = {
    "SovereignBaseAgent.py",
    "infrastructure_mixin.py",
    "healer_mixin.py",
    "mcp_hardened_mixin.py",
    "subatomic_testing_mixin.py",
    "conftest.py",
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

# Mixins that are now redundant when SovereignBaseAgent is present
REDUNDANT_MIXINS = {
    "HealerMixin",
    "MCPHardenedMixin",
    "SubatomicTestingMixin",
}


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


def has_redundant_inheritance(content: str) -> bool:
    """Check if file has classes with redundant mixin inheritance."""
    # Look for class definitions with SovereignBaseAgent and any redundant mixin
    for mixin in REDUNDANT_MIXINS:
        # Pattern: class Name(...SovereignBaseAgent...mixin...) or class Name(...mixin...SovereignBaseAgent...)
        if re.search(rf'class\s+\w+\([^)]*SovereignBaseAgent[^)]*{mixin}', content):
            return True
        if re.search(rf'class\s+\w+\([^)]*{mixin}[^)]*SovereignBaseAgent', content):
            return True
    return False


def clean_class_inheritance(content: str) -> tuple[str, int]:
    """Remove redundant mixins from class definitions.

    Returns:
        Tuple of (modified_content, number_of_cleanups)
    """
    cleanups = 0
    lines = content.split('\n')
    modified_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a class definition with inheritance
        class_match = re.match(r'^(\s*)(class\s+\w+)\(([^)]+)\)(\s*:.*)?$', line)

        if class_match:
            indent = class_match.group(1)
            class_name = class_match.group(2)
            bases_str = class_match.group(3)
            suffix = class_match.group(4) or ':'

            # Parse the bases
            bases = [b.strip() for b in bases_str.split(',')]

            # Check if SovereignBaseAgent is in the bases
            has_sovereign = any('SovereignBaseAgent' in b for b in bases)

            if has_sovereign:
                # Remove redundant mixins
                original_count = len(bases)
                bases = [b for b in bases if b not in REDUNDANT_MIXINS]

                if len(bases) < original_count:
                    cleanups += original_count - len(bases)
                    # Reconstruct the class definition
                    new_bases_str = ', '.join(bases)
                    line = f"{indent}{class_name}({new_bases_str}){suffix}"

        modified_lines.append(line)
        i += 1

    return '\n'.join(modified_lines), cleanups


def remove_unused_imports(content: str, removed_mixins: set[str]) -> tuple[str, int]:
    """Remove imports for mixins that are no longer used.

    Returns:
        Tuple of (modified_content, number_of_imports_removed)
    """
    imports_removed = 0
    lines = content.split('\n')
    modified_lines = []

    for line in lines:
        skip_line = False

        for mixin in removed_mixins:
            # Check if this line imports the mixin and mixin is not used elsewhere
            if f'import {mixin}' in line or 'from' in line and mixin in line:
                # Check if mixin is still used in the content (excluding import lines)
                content_without_imports = '\n'.join([l for l in lines if 'import' not in l])
                if mixin not in content_without_imports:
                    skip_line = True
                    imports_removed += 1
                    break

        if not skip_line:
            modified_lines.append(line)

    return '\n'.join(modified_lines), imports_removed


def process_file(file_path: Path, dry_run: bool = True) -> dict:
    """Process a single file.

    Returns:
        dict with processing results
    """
    result = {
        "file": str(file_path),
        "cleanups": 0,
        "imports_removed": 0,
        "skipped": False,
        "reason": None,
    }

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["skipped"] = True
        result["reason"] = f"Read error: {e}"
        return result

    if not has_redundant_inheritance(content):
        result["skipped"] = True
        result["reason"] = "No redundant inheritance"
        return result

    # Clean class inheritance
    modified_content, cleanups = clean_class_inheritance(content)
    result["cleanups"] = cleanups

    if cleanups == 0:
        result["skipped"] = True
        result["reason"] = "No cleanable patterns"
        return result

    # Try to remove unused imports (conservative - only if mixin is completely unused)
    modified_content, imports_removed = remove_unused_imports(modified_content, REDUNDANT_MIXINS)
    result["imports_removed"] = imports_removed

    if not dry_run:
        try:
            file_path.write_text(modified_content, encoding='utf-8')
        except Exception as e:
            result["skipped"] = True
            result["reason"] = f"Write error: {e}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Batch 4: MRO Cleanup")
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

    print(f"{'[DRY RUN]' if dry_run else '[EXECUTE]'} Phase 4 Batch 4: MRO Cleanup")
    print(f"Scanning: {root}")
    print("-" * 60)

    files = find_python_files(root)
    print(f"Found {len(files)} Python files to analyze")

    stats = {
        "files_processed": 0,
        "files_modified": 0,
        "cleanups": 0,
        "imports_removed": 0,
        "files_skipped": 0,
    }

    for file_path in files:
        result = process_file(file_path, dry_run=dry_run)
        stats["files_processed"] += 1

        if result["skipped"]:
            stats["files_skipped"] += 1
            continue

        if result["cleanups"] > 0:
            stats["files_modified"] += 1
            stats["cleanups"] += result["cleanups"]
            stats["imports_removed"] += result["imports_removed"]

            rel_path = file_path.relative_to(root.parent)
            print(f"  {'[WOULD MODIFY]' if dry_run else '[MODIFIED]'} {rel_path}")
            print(f"    - Removed {result['cleanups']} redundant mixin(s)")
            if result["imports_removed"]:
                print(f"    - Removed {result['imports_removed']} unused import(s)")

    print("-" * 60)
    print("Summary:")
    print(f"  Files processed: {stats['files_processed']}")
    print(f"  Files modified:  {stats['files_modified']}")
    print(f"  Mixins removed:  {stats['cleanups']}")
    print(f"  Imports removed: {stats['imports_removed']}")
    print(f"  Files skipped:   {stats['files_skipped']}")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
