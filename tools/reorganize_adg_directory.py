#!/usr/bin/env python3
"""Reorganize ADG directory with proper subfolder structure."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"


def create_subfolder_structure():
    """Create subfolder structure for ADG artifacts."""
    subfolders = {
        "tests": ADG_DIR / "tests",
        "cache": ADG_DIR / "cache",
        "reports": ADG_DIR / "reports"
    }

    for name, path in subfolders.items():
        path.mkdir(exist_ok=True)
        print(f"✅ Created: {name}/")

    return subfolders


def move_files_to_subfolders(subfolders):
    """Move files to appropriate subfolders."""
    moved_files = []

    # Move test files to tests/
    test_patterns = ["*test*.json", "*e2e*.json"]
    for pattern in test_patterns:
        for file_path in ADG_DIR.glob(pattern):
            if file_path.is_file():
                dest = subfolders["tests"] / file_path.name
                shutil.move(str(file_path), str(dest))
                moved_files.append(f"tests/{file_path.name}")
                print(f"  Moved: {file_path.name} -> tests/")

    # Move cache to cache/
    cache_file = ADG_DIR / "scan_result_cache.json"
    if cache_file.exists():
        dest = subfolders["cache"] / cache_file.name
        shutil.move(str(cache_file), str(dest))
        moved_files.append(f"cache/{cache_file.name}")
        print(f"  Moved: {cache_file.name} -> cache/")

    # Move precision pass reports to reports/
    report_patterns = [
        "*_20260323_*.json",  # Precision pass reports
        "adg_1653_*.json",    # Gap closure reports
        "*summary.md"         # Summary files
    ]
    for pattern in report_patterns:
        for file_path in ADG_DIR.glob(pattern):
            if file_path.is_file():
                dest = subfolders["reports"] / file_path.name
                shutil.move(str(file_path), str(dest))
                moved_files.append(f"reports/{file_path.name}")
                print(f"  Moved: {file_path.name} -> reports/")

    return moved_files


def list_remaining_files():
    """List files remaining in main ADG directory."""
    remaining = []
    for item in ADG_DIR.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            remaining.append(item.name)

    return remaining


def main():
    """Main reorganization process."""
    print("=" * 80)
    print("REORGANIZE ADG DIRECTORY")
    print("=" * 80)

    # 1. Create subfolder structure
    print("\n[1] Creating subfolder structure...")
    subfolders = create_subfolder_structure()

    # 2. Move files to subfolders
    print("\n[2] Moving files to subfolders...")
    moved = move_files_to_subfolders(subfolders)

    # 3. List remaining files
    print("\n[3] Files remaining in main adg/ directory:")
    remaining = list_remaining_files()
    for file_name in sorted(remaining):
        print(f"  - {file_name}")

    print("\n" + "=" * 80)
    print("REORGANIZATION COMPLETE")
    print("=" * 80)
    print(f"Files moved: {len(moved)}")
    print(f"Files remaining in main directory: {len(remaining)}")
    print("\n✅ ADG directory reorganized successfully!")


if __name__ == "__main__":
    main()
