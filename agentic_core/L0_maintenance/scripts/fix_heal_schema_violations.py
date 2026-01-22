"""
Automated Fix: Replace non-canonical keys with canonical equivalents

This script reads the violations from .schema_violations_tracking.yaml
and automatically fixes them by replacing non-canonical keys.

USAGE:
    python scripts/maintenance/fix_heal_schema_violations.py
    python scripts/maintenance/fix_heal_schema_violations.py --dry-run
"""

from pathlib import Path
import argparse
import re
import yaml


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
            pattern = f"""(['\\"]){old_key}\\1\\s*:"""
            replacement = f"\\1{new_key}\\1:"
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                replacement_count += count
        if content != original_content:
            filepath.write_text(content, encoding="utf-8")
            return (True, replacement_count)
        return (False, 0)
    except Exception:
        return (False, 0)


def main():
    """TODO: Add documentation for main."""
    parser = argparse.ArgumentParser(description="Fix @standard_heal schema violations")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without modifying files"
    )
    args = parser.parse_args()
    tracking_file = Path(".schema_violations_tracking.yaml")
    if not tracking_file.exists():
        return 1
    with open(tracking_file) as f:
        tracking = yaml.safe_load(f)
    violations = tracking.get("violations", [])
    total_files_modified = 0
    total_replacements = 0
    for violation in violations:
        filepath = Path(violation["file"])
        if not filepath.exists():
            continue
        replacements = {}
        for v in violation["violations"]:
            if v["status"] == "pending":
                replacements[v["key"]] = v["canonical"]
        if not replacements:
            continue
        if args.dry_run:
            for old, new in replacements.items():
                pass
        else:
            modified, count = fix_file(filepath, replacements)
            if modified:
                total_files_modified += 1
                total_replacements += count
    if args.dry_run:
        pass
    return 0


if __name__ == "__main__":
    exit(main())
