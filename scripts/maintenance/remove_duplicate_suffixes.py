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
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Common problematic suffixes that indicate duplicates
PROBLEMATIC_SUFFIXES = [
    "_flat",
    "_from_utils",
    "_1", "_2", "_3",  # Numbered variants
    "_copy", "_backup",
    "_old", "_new",
    "_temp", "_tmp",
]


def find_duplicate_files() -> list[Path]:
    """Find all files with problematic suffixes."""
    all_duplicates = []
    
    for suffix in PROBLEMATIC_SUFFIXES:
        pattern = f"*{suffix}.py"
        files = list(project_root.rglob(pattern))
        # Exclude archives
        files = [f for f in files if "archives" not in str(f)]
        all_duplicates.extend(files)
    
    return all_duplicates


def get_canonical_path(duplicate_path: Path) -> tuple[Path, str | None]:
    """Get the canonical path by removing suffix.
    
    Returns:
        Tuple of (canonical_path, matched_suffix)
    """
    stem = duplicate_path.stem
    
    # Check which suffix matches
    for suffix in PROBLEMATIC_SUFFIXES:
        if stem.endswith(suffix):
            canonical_stem = stem[:-len(suffix)]
            canonical_path = duplicate_path.parent / f"{canonical_stem}.py"
            return canonical_path, suffix
    
    return duplicate_path, None


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
    results = {
        "safe_to_delete": [],
        "needs_review": [],
    }
    
    for dup_path in duplicate_files:
        canonical_path, suffix = get_canonical_path(dup_path)
        
        if suffix is None:
            # Not a recognized suffix pattern, skip
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
    
    for dup_path, canonical_path, suffix, _ in safe_to_delete:
        rel_dup = dup_path.relative_to(project_root)
        rel_canonical = canonical_path.relative_to(project_root)
        
        if dry_run:
            print(f"  [DRY-RUN] Would delete: {rel_dup} (suffix: {suffix})")
            print(f"            Canonical exists: {rel_canonical}")
        else:
            try:
                dup_path.unlink()
                print(f"  ✓ Deleted: {rel_dup} (suffix: {suffix})")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to delete {rel_dup}: {e}")
    
    return removed_count


def main(dry_run: bool = True) -> int:
    """
    Main execution.
    
    Returns:
        Exit code (0 for success)
    """
    print("\n" + "=" * 70)
    print("INTELLIGENT DUPLICATE SUFFIX REMOVAL TOOL")
    print("=" * 70)
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'EXECUTE (will delete files)'}")
    print(f"Detecting suffixes: {', '.join(PROBLEMATIC_SUFFIXES)}")
    print("=" * 70)
    
    # Find duplicates
    print("\n[1] Scanning for duplicate files with problematic suffixes...")
    duplicate_files = find_duplicate_files()
    
    print(f"    Found {len(duplicate_files)} files with problematic suffixes")
    
    # Analyze
    print("\n[2] Analyzing duplicates...")
    results = analyze_duplicates(duplicate_files)
    
    safe_count = len(results["safe_to_delete"])
    review_count = len(results["needs_review"])
    
    # Count by suffix type
    suffix_breakdown = {}
    for _, _, suffix, _ in results["safe_to_delete"]:
        suffix_breakdown[suffix] = suffix_breakdown.get(suffix, 0) + 1
    
    print(f"    Safe to delete: {safe_count} (canonical exists)")
    print(f"    Breakdown by suffix: {suffix_breakdown}")
    print(f"    Needs review: {review_count} (no canonical)")
    
    # Remove safe duplicates
    if safe_count > 0:
        print(f"\n[3] {'Previewing' if dry_run else 'Removing'} safe duplicates...")
        removed = remove_duplicates(results["safe_to_delete"], dry_run)
        
        if not dry_run:
            print(f"\n✓ Removed {removed} duplicate files")
    
    # Report files needing review
    if review_count > 0:
        print(f"\n[4] Files needing manual review ({review_count}):")
        for dup_path, canonical_path, suffix, _ in results["needs_review"]:
            rel_dup = dup_path.relative_to(project_root)
            rel_canonical = canonical_path.relative_to(project_root)
            print(f"    • {rel_dup} (suffix: {suffix})")
            print(f"      → Should rename to: {rel_canonical}")
    
    # Summary
    print("\n" + "=" * 70)
    if dry_run:
        print("DRY-RUN COMPLETE")
        print(f"  Would delete: {safe_count} files")
        print(f"  Suffix breakdown: {suffix_breakdown}")
        print(f"  Manual review: {review_count} files")
        print("\nRun with --execute to perform actual deletion")
    else:
        print("CLEANUP COMPLETE")
        print(f"  Deleted: {removed} files")
        print(f"  Suffix breakdown: {suffix_breakdown}")
        print(f"  Manual review: {review_count} files")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Remove duplicate files with _flat and _1 suffixes")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (default is dry-run)",
    )
    
    args = parser.parse_args()
    
    sys.exit(main(dry_run=not args.execute))
