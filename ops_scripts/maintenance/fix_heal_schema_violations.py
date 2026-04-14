#!/usr/bin/env python3
"""
Automated Fix: Replace non-canonical keys with canonical equivalents

This script reads the violations from .schema_violations_tracking.yaml
and automatically fixes them by replacing non-canonical keys.

USAGE:
    python scripts/maintenance/fix_heal_schema_violations.py
    python scripts/maintenance/fix_heal_schema_violations.py --dry-run
"""

import argparse
import re
from pathlib import Path

import yaml
from tqdm import tqdm


def fix_file(filepath: Path, replacements: dict[str, str]) -> tuple[bool, int]:
    """
    Fix non-canonical keys in a file.

    Args:
        filepath: Path to file to fix
        replacements: Dict of {old_key: new_key}

    Returns:
        Tuple of (modified, count_of_replacements)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        original_content = content
        replacement_count = 0

        for old_key, new_key in replacements.items():
            # Pattern: 'old_key': value or "old_key": value
            pattern = rf"(['\"]){old_key}\1\s*:"
            replacement = rf"\1{new_key}\1:"

            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                replacement_count += count
                print(f"    Replaced '{old_key}' → '{new_key}' ({count} occurrences)")

        if content != original_content:
            filepath.write_text(content, encoding="utf-8")
            return True, replacement_count

        return False, 0

    except Exception as e:
        raise
        print(f"  ❌ Error fixing {filepath}: {e}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(description="Fix @standard_heal schema violations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without modifying files",
    )
    args = parser.parse_args()

    # Load tracking file
    tracking_file = Path(".schema_violations_tracking.yaml")
    if not tracking_file.exists():
        print("❌ Tracking file not found: .schema_violations_tracking.yaml")
        return 1

    with open(tracking_file) as f:
        tracking = yaml.safe_load(f)

    violations = tracking.get("violations", [])

    print(f"\n{'=' * 70}")
    print("schema Violation Auto-Fix")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}")
    print(f"Total files to process: {len(violations)}")
    print(f"{'=' * 70}\n")

    total_files_modified = 0
    total_replacements = 0

    for violation in tqdm(violations, desc="Processing", unit="item"):
        filepath = Path(violation["file"])

        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        # Build replacements dict
        replacements = {}
        for v in violation["violations"]:
            if v["status"] == "pending":
                replacements[v["key"]] = v["canonical"]

        if not replacements:
            continue

        print(f"\n📝 {filepath}")

        if args.dry_run:
            print("  [DRY RUN] Would replace:")
            for old, new in replacements.items():
                print(f"    '{old}' → '{new}'")
        else:
            modified, count = fix_file(filepath, replacements)
            if modified:
                total_files_modified += 1
                total_replacements += count
                print(f"  ✅ Fixed ({count} replacements)")
            else:
                print("  ⚠️  No changes made (patterns not found)")

    print(f"\n{'=' * 70}")
    if args.dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would modify {len([v for v in violations if v['violations']])} files")
    else:
        print("FIX COMPLETE")
        print(f"Files modified: {total_files_modified}")
        print(f"Total replacements: {total_replacements}")
        print("\nNext steps:")
        print("  1. Run: python scripts/maintenance/check_heal_schema_compliance.py")
        print("  2. Run tests: pytest tests/L5_safety/test_hygiene_consolidation.py")
        print("  3. Update .schema_violations_tracking.yaml status to 'fixed'")
    print(f"{'=' * 70}\n")

    return 0


if __name__ == "__main__":
    exit(main())
