"""
Remove Duplicate Files with Problematic Suffixes

RCA: These duplicates were created during Phase 1-8 architectural sovereignty work.
The flattening process created duplicates instead of consolidating to single canonical files.

Enhanced with intelligent suffix detection to catch all common patterns:
_flat, _from_utils, _1, _2, _copy, _backup, etc.

This script:
1. Identifies all files with problematic suffixes
2. Checks if canonical version (without suffix) exists
3. Removes duplicate if canonical exists
4. Reports files that need manual review
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
PROBLEMATIC_SUFFIXES = [
    "_flat",
    "_from_utils",
    "_1",
    "_2",
    "_3",
    "_copy",
    "_backup",
    "_old",
    "_new",
    "_temp",
    "_tmp",
]


def find_duplicate_files() -> list[Path]:
    """Find all files with problematic suffixes."""
    all_duplicates = []
    for suffix in PROBLEMATIC_SUFFIXES:
        pattern = f"*{suffix}.py"
        files = list(project_root.rglob(pattern))
        files = [f for f in files if "archives" not in str(f)]
        all_duplicates.extend(files)
    return all_duplicates


def get_canonical_path(duplicate_path: Path) -> tuple[Path, str | None]:
    """Get the canonical path by removing suffix.

    Returns:
        Tuple of (canonical_path, matched_suffix)
    """
    stem = duplicate_path.stem
    for suffix in PROBLEMATIC_SUFFIXES:
        if stem.endswith(suffix):
            canonical_stem = stem[: -len(suffix)]
            canonical_path = duplicate_path.parent / f"{canonical_stem}.py"
            return (canonical_path, suffix)
    return (duplicate_path, None)


def analyze_duplicates(
    duplicate_files: list[Path],
) -> dict[str, list[tuple[Path, Path, str, bool]]]:
    """
    Analyze duplicates and categorize them.

    Returns:
        Dict with categories:
        - safe_to_delete: Canonical exists, duplicate can be removed
        - needs_review: Canonical doesn't exist, need to rename

    Each entry is (dup_path, canonical_path, suffix, canonical_exists)
    """
    results = {"safe_to_delete": [], "needs_review": []}
    for dup_path in duplicate_files:
        canonical_path, suffix = get_canonical_path(dup_path)
        if suffix is None:
            continue
        canonical_exists = canonical_path.exists()
        if canonical_exists:
            results["safe_to_delete"].append((dup_path, canonical_path, suffix, True))
        else:
            results["needs_review"].append((dup_path, canonical_path, suffix, False))
    return results


def remove_duplicates(safe_to_delete: list[tuple[Path, Path, str, bool]], dry_run: bool = True) -> int:
    """Remove duplicate files that have canonical versions."""
    removed_count = 0
    for dup_path, canonical_path, _suffix, _ in safe_to_delete:
        dup_path.relative_to(project_root)
        canonical_path.relative_to(project_root)
        if dry_run:
            pass
        else:
            try:
                dup_path.unlink()
                removed_count += 1
            except Exception:
                pass
    return removed_count


def main(dry_run: bool = True) -> int:
    """
    Main execution.

    Returns:
        Exit code (0 for success)
    """
    duplicate_files = find_duplicate_files()
    results = analyze_duplicates(duplicate_files)
    safe_count = len(results["safe_to_delete"])
    review_count = len(results["needs_review"])
    suffix_breakdown = {}
    for _, _, suffix, _ in results["safe_to_delete"]:
        suffix_breakdown[suffix] = suffix_breakdown.get(suffix, 0) + 1
    if safe_count > 0:
        remove_duplicates(results["safe_to_delete"], dry_run)
        if not dry_run:
            pass
    if review_count > 0:
        for dup_path, canonical_path, suffix, _ in results["needs_review"]:
            dup_path.relative_to(project_root)
            canonical_path.relative_to(project_root)
    if dry_run:
        pass
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remove duplicate files with _flat and _1 suffixes")
    parser.add_argument("--execute", action="store_true", help="Actually delete files (default is dry-run)")
    args = parser.parse_args()
    sys.exit(main(dry_run=not args.execute))
