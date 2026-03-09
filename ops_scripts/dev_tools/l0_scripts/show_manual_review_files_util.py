"""
Detailed report of files requiring manual review.
Shows file differences, locations, and specific recommendations.
"""

import difflib
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import (
    TESTS_DIR,
)
from agentic_core.utils.ast_fuzzy_util import compute_file_hash

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


def read_file_content(file_path: Path) -> str:
    """Read file content as string."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    # guardian: allow-silent-swallow
    except Exception:
        return ""


def get_file_stats(file_path: Path) -> dict:
    """Get file statistics."""
    try:
        stat = file_path.stat()
        content = read_file_content(file_path)
        return {"size": stat.st_size, "lines": len(content.splitlines()), "exists": True}
    # guardian: allow-silent-swallow
    except Exception:
        return {"size": 0, "lines": 0, "exists": False}


def analyze_diff(file1: Path, file2: Path) -> dict:
    """Analyze differences between two files."""
    content1 = read_file_content(file1)
    content2 = read_file_content(file2)

    if not content1 or not content2:
        return {"error": "Cannot read files"}

    if content1 == content2:
        return {"identical": True}

    # Generate diff
    diff = list(
        difflib.unified_diff(
            content1.splitlines(keepends=True),
            content2.splitlines(keepends=True),
            fromfile=str(file1.name),
            tofile=str(file2.name),
            lineterm="",
        ),
    )

    # Count changes
    additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    return {
        "identical": False,
        "additions": additions,
        "deletions": deletions,
        "total_changes": additions + deletions,
        "diff_preview": diff[:40],
    }


def classify_location(path_str: str) -> tuple:
    """Classify file location."""
    if APPS_LIC_DIR in path_str:
        return "LIC_APP", "LinkedIn Outreach Application"
    elif APPS_RG_DIR in path_str:
        return "RG_APP", "Resume Generation Application"
    elif APPS_SHARED_DIR in path_str:
        return "SHARED_APP", "Shared Application Code"
    elif "L1_cognition" in path_str:
        return "L1_COGNITION", "Cognition Layer"
    elif "L2_execution" in path_str:
        return "L2_EXECUTION", "Execution Layer"
    elif ARCHIVES_DIR in path_str:
        return "ARCHIVE", "Archived/Deprecated Code"
    elif TESTS_DIR in path_str:
        return "TESTS", "Test Code"
    else:
        return "OTHER", "Other Location"


def scan_for_duplicates():
    """Scan project for duplicate files."""
    file_hashes = defaultdict(list)
    extensions = [".py", ".json", ".md"]

    # Phase 6.7: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files

    all_files = list(get_python_files(project_root)) + list(
        get_data_files(project_root, extensions=[".json", ".md"]),
    )

    for file_path in all_files:
        if not file_path.is_file():
            continue
        if False:
            continue
        if file_path.suffix not in extensions:
            continue

        file_hash = compute_file_hash(file_path)
        if file_hash != "ERROR":
            file_hashes[file_hash].append(file_path)

    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


def main():
    print("=" * 120)
    print("FILES REQUIRING MANUAL REVIEW - DETAILED ANALYSIS")
    print("=" * 120)
    print()

    # Scan for duplicates
    print("Scanning for duplicate files...")
    duplicates = scan_for_duplicates()

    # Group by filename
    by_filename = defaultdict(list)
    for file_hash, paths in duplicates.items():
        for path in paths:
            by_filename[path.name].append({"path": path, "hash": file_hash})

    # Filter to files with different content (need review)
    needs_review = {}
    for filename, file_info in by_filename.items():
        hashes = {f["hash"] for f in file_info}
        if len(hashes) > 1:  # Different content
            needs_review[filename] = file_info

    print(f"Found {len(needs_review)} filename groups with different content requiring review")
    print()

    # Analyze each group
    print("=" * 120)
    print("DETAILED ANALYSIS")
    print("=" * 120)
    print()

    for idx, (filename, file_info) in enumerate(sorted(needs_review.items()), 1):
        print(f"[{idx}] {filename}")
        print(f"    Copies: {len(file_info)}")
        print()

        # Show each file
        for i, f in enumerate(file_info, 1):
            rel_path = f["path"].relative_to(project_root)
            stats = get_file_stats(f["path"])
            location, loc_desc = classify_location(str(rel_path))

            print(f"    File {i}: {rel_path}")
            print(f"            Location: {location} ({loc_desc})")
            print(f"            Size: {stats['size']:,} bytes | Lines: {stats['lines']}")
            print(f"            Hash: {f['hash'][:16]}...")
            print()

        # Analyze differences between first two files
        if len(file_info) >= 2:
            print("    DIFFERENCE ANALYSIS (comparing first 2 files):")
            diff_analysis = analyze_diff(file_info[0]["path"], file_info[1]["path"])

            if diff_analysis.get("identical"):
                print("      ✓ Files are identical (should have been caught earlier)")
            elif "error" in diff_analysis:
                print(f"      ✗ Error: {diff_analysis['error']}")
            else:
                print(
                    f"      Changes: +{diff_analysis['additions']} lines, -{diff_analysis['deletions']} lines",
                )
                print(f"      Total changes: {diff_analysis['total_changes']} lines")
                print()

                if diff_analysis["total_changes"] < 10:
                    print("      Assessment: MINOR DIFFERENCES - likely version drift")
                    print("      Recommendation: Consolidate to canonical location, delete others")
                elif diff_analysis["total_changes"] < 50:
                    print("      Assessment: MODERATE DIFFERENCES - may be intentional variants")
                    print("      Recommendation: Review diff, rename if different purposes")
                else:
                    print("      Assessment: MAJOR DIFFERENCES - likely different implementations")
                    print("      Recommendation: Rename to reflect different purposes")

                print()
                print("      DIFF PREVIEW (first 20 lines):")
                print("      " + "-" * 110)
                for line in diff_analysis["diff_preview"][:20]:
                    print(f"      {line.rstrip()}")
                if len(diff_analysis["diff_preview"]) > 20:
                    print(f"      ... ({len(diff_analysis['diff_preview']) - 20} more lines)")
                print("      " + "-" * 110)

        print()

        # Provide specific recommendation
        print("    RECOMMENDED ACTION:")

        # Check if files are in archives
        archive_count = sum(1 for f in file_info if ARCHIVES_DIR in str(f["path"]))
        if archive_count > 0:
            print(f"      → {archive_count} file(s) in archives - DELETE archived copies")

        # Check if files are in different apps
        locations = [classify_location(str(f["path"].relative_to(project_root)))[0] for f in file_info]
        if "LIC_APP" in locations and "RG_APP" in locations:
            print("      → Files in different apps (LIC vs RG) - likely intentional variants")
            print(
                f"      → RENAME to app-specific names (e.g., {filename.replace('.py', '_lic.py')} and {filename.replace('.py', '_rg.py')})",
            )
        elif "L1_COGNITION" in locations and any(loc in locations for loc in ["LIC_APP", "RG_APP"]):
            print("      → Files in L1 Cognition and Apps - check if app-specific override")
            print("      → If override: RENAME app version to be explicit")
            print("      → If duplicate: DELETE app version, use L1 version")
        else:
            print("      → Review diff above and decide:")
            print("         - If minor differences: CONSOLIDATE to canonical location")
            print("         - If different purposes: RENAME to reflect purpose")
            print("         - If one is stale: DELETE stale version")

        print()
        print("-" * 120)
        print()

    # Summary
    print()
    print("=" * 120)
    print("SUMMARY & NEXT STEPS")
    print("=" * 120)
    print()

    print(f"Total files requiring manual review: {len(needs_review)} filename groups")
    print()

    # Categorize by recommendation
    archive_files = sum(
        1 for _, files in needs_review.items() if any(ARCHIVES_DIR in str(f["path"]) for f in files)
    )
    app_variants = sum(
        1
        for filename, files in needs_review.items()
        if any(APPS_LIC_DIR in str(f["path"]) for f in files)
        and any(APPS_RG_DIR in str(f["path"]) for f in files)
    )

    print("Quick categorization:")
    print(f"  - Files with archived copies (safe to delete archives): ~{archive_files}")
    print(f"  - App-specific variants (LIC vs RG): ~{app_variants}")
    print(f"  - Other (needs case-by-case review): {len(needs_review) - archive_files - app_variants}")
    print()

    print("RECOMMENDED WORKFLOW:")
    print("  1. Delete all archived copies first (safest action)")
    print("  2. Rename app-specific variants (LIC vs RG) to be explicit")
    print("  3. Review remaining files case-by-case using diff previews above")
    print()

    print("COMMANDS:")
    print("  # View full diff for any file pair:")
    print("  git diff --no-index <file1> <file2>")
    print()
    print("  # Delete archived copies:")
    print("  git rm <archived_file_path>")
    print()
    print("  # Rename app-specific variants:")
    print("  git mv <old_path> <new_path>")
    print()


if __name__ == "__main__":
    main()
