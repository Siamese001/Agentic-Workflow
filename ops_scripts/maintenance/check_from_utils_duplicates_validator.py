"""
Quick script to check _from_utils duplicates.
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, get_validated_project_root

PROJECT_ROOT = get_validated_project_root()


def find_from_utils_duplicates(project_root: Path) -> list[tuple[Path, Path]]:
    """Return duplicate *_from_utils.py files that have a canonical sibling."""
    duplicates: list[tuple[Path, Path]] = []

    for candidate in sorted(project_root.rglob("*_from_utils.py")):
        if ARCHIVES_DIR in candidate.parts:
            continue

        canonical = candidate.parent / candidate.name.replace("_from_utils.py", ".py")
        if canonical.exists():
            duplicates.append((candidate, canonical))

    return duplicates


def main() -> int:
    duplicates = find_from_utils_duplicates(PROJECT_ROOT)
    print(f"Total _from_utils files with canonical versions: {len(duplicates)}")

    if duplicates:
        print("\nDuplicates found:")
        for duplicate, canonical in duplicates:
            print(f"  {duplicate.relative_to(PROJECT_ROOT)} -> {canonical.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
