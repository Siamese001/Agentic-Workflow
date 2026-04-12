#!/usr/bin/env python3
"""Clean up ADG directory - keep only latest files and organize properly."""

import shutil
from pathlib import Path


def cleanup_adg_directory():
    """Clean up ADG directory structure."""
    adg_dir = Path("C:/Git/Agentic-Workflow/artifacts/adg")

    print("ADG Directory Cleanup")
    print("=" * 50)

    # 1. Ensure proper directory structure
    subdirs = ["databases", "graphs", "reports", "archives", "cache", "_archive"]
    for subdir in subdirs:
        (adg_dir / subdir).mkdir(exist_ok=True)

    # 2. Move any loose files to appropriate locations
    # Move SQLite files
    for sqlite_file in adg_dir.glob("*.sqlite"):
        target = adg_dir / "databases" / sqlite_file.name
        if sqlite_file != target:
            print(f"Moving {sqlite_file.name} -> databases/")
            shutil.move(str(sqlite_file), str(target))

    # Move JSON files (non-report)
    for json_file in adg_dir.glob("*.json"):
        # Skip if already in subdirectory
        if any(parent.name in subdirs for parent in json_file.parents):
            continue

        # Determine where to put it
        if "report" in json_file.name.lower():
            target_dir = adg_dir / "reports"
        elif "graph" in json_file.name.lower():
            target_dir = adg_dir / "graphs"
        else:
            target_dir = adg_dir / "reports"  # Default to reports

        target = target_dir / json_file.name
        if json_file != target:
            print(f"Moving {json_file.name} -> {target_dir.name}/")
            shutil.move(str(json_file), str(target))

    # 3. Clean up old archives (keep only latest 5)
    archive_dir = adg_dir / "_archive" / "2026-03"
    if archive_dir.exists():
        # Get all files and sort by modification time
        files = []
        for file in archive_dir.glob("*"):
            if file.is_file():
                files.append((file.stat().st_mtime, file))

        # Sort by time (newest first)
        files.sort(reverse=True)

        # Remove old files beyond latest 5 of each type
        file_types = {}
        for mtime, file in files:
            prefix = file.name.split("_")[0] + "_" + file.name.split("_")[1]
            if prefix not in file_types:
                file_types[prefix] = []
            file_types[prefix].append((mtime, file))

        removed_count = 0
        for prefix, type_files in file_types.items():
            # Keep only latest 5 of each type
            for mtime, file in type_files[5:]:
                print(f"Removing old archive: {file.name}")
                file.unlink()
                removed_count += 1

        print(f"Removed {removed_count} old archive files")

    # 4. Verify latest files are in place
    latest_timestamp = "03222026_1653"

    # Check database
    db_path = adg_dir / "databases" / f"adg_indexed_{latest_timestamp}.sqlite"
    if db_path.exists():
        print(f"✓ Latest database found: {db_path.name}")
    else:
        print(f"✗ Latest database missing: {db_path.name}")

    # Check graphs
    graph_files = [
        f"adg_file_graph_{latest_timestamp}.json",
        f"adg_symbol_graph_{latest_timestamp}.json",
        f"adg_governance_graph_{latest_timestamp}.json",
        f"adg_snapshot_{latest_timestamp}.json",
    ]

    for graph_file in graph_files:
        graph_path = adg_dir / "graphs" / graph_file
        if graph_path.exists():
            print(f"✓ Latest graph found: {graph_file}")
        else:
            print(f"✗ Latest graph missing: {graph_file}")

    # Check archive
    zip_path = adg_dir / "archives" / f"adg_run_{latest_timestamp}.zip"
    if zip_path.exists():
        print(f"✓ Latest archive found: {zip_path.name}")
    else:
        print(f"✗ Latest archive missing: {zip_path.name}")

    # 5. Show final directory structure
    print("\nFinal Directory Structure:")
    print("-" * 30)
    for subdir in subdirs:
        subdir_path = adg_dir / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob("*"))
            print(f"{subdir}/: {len(files)} files")

    print("\n✅ ADG directory cleanup complete!")


if __name__ == "__main__":
    cleanup_adg_directory()
