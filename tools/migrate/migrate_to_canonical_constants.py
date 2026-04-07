#!/usr/bin/env python3
"""
Constants Migration Script

Migrates duplicated constants (MAX_RETRIES, DEFAULT_SLEEP, etc.) from inline
definitions to canonical SSOT imports from agentic_core.config.constants_config

Usage:
    python tools/migrate_to_canonical_constants.py --check          # Dry run, show what would change
    python tools/migrate_to_canonical_constants.py --apply         # Apply changes
    python tools/migrate_to_canonical_constants.py --files file1.py file2.py  # Specific files
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# The 8 constants to migrate
CANONICAL_CONSTANTS = [
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
]

# Pattern to match constant definitions like: MAX_RETRIES = 3
CONSTANT_PATTERN = re.compile(rf'^({"|".join(CANONICAL_CONSTANTS)})\s*=\s*[^#\n]+', re.MULTILINE)

# Import statement to add
CANONICAL_IMPORT = "from agentic_core.config.constants_config import "


def find_constant_definitions(filepath: Path) -> List[Tuple[int, str, str]]:
    """Find all constant definitions in a file.

    Returns list of (line_number, constant_name, full_line)
    """
    results = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        for const in CANONICAL_CONSTANTS:
            # Match lines like: MAX_RETRIES = 3  or  MAX_RETRIES: int = 3
            if re.match(rf'^\s*{const}\s*[=:]\s*[^#\n]+', line):
                results.append((i, const, line))
                break

    return results


def has_canonical_import(content: str) -> bool:
    """Check if file already imports from canonical module."""
    return 'from agentic_core.config.constants_config import' in content


def migrate_file(filepath: Path, dry_run: bool = True) -> dict:
    """Migrate a single file.

    Returns dict with migration details.
    """
    content = filepath.read_text(encoding='utf-8')
    original_content = content

    # Find constant definitions
    definitions = find_constant_definitions(filepath)
    if not definitions:
        return {'file': str(filepath), 'changed': False, 'constants_found': 0}

    constants_to_import = set(d[1] for d in definitions)

    # Check if already has canonical import
    already_imports = has_canonical_import(content)

    # Remove constant definitions
    lines = content.split('\n')
    new_lines = []
    removed_lines = []

    for i, line in enumerate(lines, 1):
        should_remove = False
        for const in CANONICAL_CONSTANTS:
            if re.match(rf'^\s*{const}\s*[=:]\s*[^#\n]+', line):
                should_remove = True
                removed_lines.append((i, line))
                break
        if not should_remove:
            new_lines.append(line)

    content = '\n'.join(new_lines)

    # Add import if not already present
    if not already_imports and constants_to_import:
        # Find a good place to add import (after other imports, before code)
        import_idx = 0
        for i, line in enumerate(new_lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1

        import_line = f"{CANONICAL_IMPORT}{', '.join(sorted(constants_to_import))}"
        new_lines.insert(import_idx, import_line)
        content = '\n'.join(new_lines)

    changed = content != original_content

    if not dry_run and changed:
        filepath.write_text(content, encoding='utf-8')

    return {
        'file': str(filepath),
        'changed': changed,
        'constants_found': len(definitions),
        'constants': sorted(constants_to_import),
        'already_had_import': already_imports,
        'removed_lines': removed_lines,
    }


def main():
    parser = argparse.ArgumentParser(description='Migrate constants to SSOT')
    parser.add_argument('--check', action='store_true', help='Dry run - show what would change')
    parser.add_argument('--apply', action='store_true', help='Apply changes')
    parser.add_argument('--files', nargs='+', help='Specific files to migrate')
    parser.add_argument('--batch-size', type=int, default=50, help='Max files to process')

    args = parser.parse_args()

    if not args.check and not args.apply and not args.files:
        parser.print_help()
        sys.exit(1)

    dry_run = not args.apply

    # Get files to process
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        # Find all Python files in agentic_core that might have constants
        files = list(Path('agentic_core').rglob('*.py'))
        files = [f for f in files if f.is_file()]

    if args.batch_size:
        files = files[:args.batch_size]

    # Process files
    results = []
    for filepath in files:
        try:
            result = migrate_file(filepath, dry_run=dry_run)
            if result['changed'] or result['constants_found'] > 0:
                results.append(result)
        except Exception as e:
            results.append({'file': str(filepath), 'error': str(e)})

    # Summary
    changed_files = [r for r in results if r.get('changed')]
    total_constants = sum(r.get('constants_found', 0) for r in results)

    print(f"\n{'='*60}")
    print(f"Migration Summary ({'DRY RUN' if dry_run else 'APPLIED'})")
    print(f"{'='*60}")
    print(f"Files processed: {len(files)}")
    print(f"Files with constants: {len(results)}")
    print(f"Files changed: {len(changed_files)}")
    print(f"Total constants found: {total_constants}")

    if changed_files:
        print("\nChanged files:")
        for r in changed_files[:20]:  # Show first 20
            print(f"  - {r['file']}: {r['constants']}")
        if len(changed_files) > 20:
            print(f"  ... and {len(changed_files) - 20} more")

    return results


if __name__ == '__main__':
    main()
