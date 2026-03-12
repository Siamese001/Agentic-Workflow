#!/usr/bin/env python3
"""
Simple string-based threshold refactoring.

Replaces hardcoded THRESHOLD = 0.95 with import from path_constants.
Uses regex for reliability over AST transformation.
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


def refactor_file(file_path: Path, dry_run: bool = True) -> dict:
    """Refactor a single file using string replacement."""
    try:
        source = file_path.read_text(encoding='utf-8')
        original = source

        # Skip if this IS the path_constants.py file (SSOT source)
        if file_path.name == 'path_constants.py' and 'L0_routing' in str(file_path):
            return {'status': 'skipped', 'reason': 'ssot_source'}

        # Check if already imports THRESHOLD from path_constants
        has_import = 'from agentic_core.L0_routing.config.path_constants import' in source
        has_threshold_import = has_import and 'THRESHOLD' in source

        # Pattern 1: Remove standalone THRESHOLD = 0.95 lines
        # Only if we're going to add the import
        if not has_threshold_import:
            source = re.sub(
                r'^THRESHOLD\s*=\s*0\.95\s*$',
                '',
                source,
                flags=re.MULTILINE
            )

        # Pattern 2: Replace threshold=0.95 in function calls
        source = re.sub(
            r'\bthreshold\s*=\s*0\.95\b',
            'threshold=THRESHOLD',
            source
        )

        # Add import if needed and modifications were made
        if source != original and not has_threshold_import:
            # Find insertion point after imports
            lines = source.splitlines(keepends=True)
            insert_pos = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_pos = i + 1
                elif insert_pos > 0 and stripped and not stripped.startswith('#'):
                    # Found first non-import, non-comment line
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, 'from agentic_core.L0_routing.config.path_constants import THRESHOLD\n')
                source = ''.join(lines)

        if source == original:
            return {'status': 'skipped', 'reason': 'no_changes'}

        if not dry_run:
            file_path.write_text(source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'dry_run': dry_run,
        }

    except Exception as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
        }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load violations
    violations = []
    with open(baseline_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[:args.limit]

    print(f"[INFO] Processing {len(unique_files)} files")
    print(f"[MODE] {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        result = refactor_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            print(f"✓ {result['file']}")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print()
    print(f"[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")

    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
