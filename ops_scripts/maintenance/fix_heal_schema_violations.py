#!/usr/bin/env python3
"""
Automated Fix: Replace non-canonical keys with canonical equivalents.
"""

import argparse
import re
from pathlib import Path

import yaml
from tqdm import tqdm


def fix_file(filepath: Path, replacements: dict[str, str], dry_run: bool = False) -> tuple[bool, int]:
    """Fix non-canonical keys in a file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original_content = content
        replacement_count = 0

        for old_key, new_key in replacements.items():
            pattern = rf"(['\"]){old_key}\1\s*:"
            replacement = rf"\1{new_key}\1:"
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                replacement_count += count
                print(f"    Replaced '{old_key}' → '{new_key}' ({count} occurrences)")

        if content != original_content:
            if not dry_run:
                filepath.write_text(content, encoding="utf-8")
            return True, replacement_count

        return False, 0

    except (OSError, UnicodeDecodeError) as exc:
        print(f"  ❌ Error fixing {filepath}: {exc}")
        return False, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix @standard_heal schema violations")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without modifying files"
    )
    args = parser.parse_args()

    tracking_file = Path(".schema_violations_tracking.yaml")
    if not tracking_file.exists():
        print("❌ Tracking file not found: .schema_violations_tracking.yaml")
        return 1

    with tracking_file.open(encoding="utf-8") as handle:
        tracking = yaml.safe_load(handle) or {}

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

        replacements = {v["key"]: v["canonical"] for v in violation["violations"] if v["status"] == "pending"}
        if not replacements:
            continue

        print(f"\n📝 {filepath}")
        if args.dry_run:
            print("  [DRY RUN] Would replace:")
            for old, new in replacements.items():
                print(f"    '{old}' → '{new}'")
            modified, count = fix_file(filepath, replacements, dry_run=True)
        else:
            modified, count = fix_file(filepath, replacements, dry_run=False)

        if modified:
            total_files_modified += 1
            total_replacements += count
            print(f"  ✅ Fixed ({count} replacements)")
        else:
            print("  ⚠️  No changes made (patterns not found)")

    print(f"\n{'=' * 70}")
    if args.dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would modify {total_files_modified} files")
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
    raise SystemExit(main())
