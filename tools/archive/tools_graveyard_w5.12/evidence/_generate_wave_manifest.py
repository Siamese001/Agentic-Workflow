"""Generate wave manifests for narrows_possible burndown.

Usage:
    python tools/evidence/_generate_wave_manifest.py <wave_name> <directory_pattern>
    python tools/evidence/_generate_wave_manifest.py W5c.1 tools/
    python tools/evidence/_generate_wave_manifest.py W5c.2 ops_scripts/
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

SUBCATEGORIZED_PATH = Path("artifacts/adg_analysis/broad_exception_catch_subcategorized.json")
WAVE_OUTPUT_DIR = Path("artifacts/adg_analysis/waves")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python _generate_wave_manifest.py <wave_name> <directory_pattern> [--max-files N]")
        print("Example: python _generate_wave_manifest.py W5c.1 tools/ --max-files 50")
        sys.exit(1)

    wave_name = sys.argv[1]
    dir_pattern = sys.argv[2].rstrip("/")
    max_files = 50
    if len(sys.argv) > 3 and sys.argv[3] == "--max-files":
        max_files = int(sys.argv[4])

    entries = json.loads(SUBCATEGORIZED_PATH.read_text())
    narrows = [e for e in entries if e.get("sub_category") == "narrows_possible"]

    # Filter by directory pattern
    wave_entries = [e for e in narrows if dir_pattern in e["source_file"]]

    if not wave_entries:
        print(f"No narrows_possible entries found matching {dir_pattern}")
        sys.exit(0)

    # Group by file
    by_file = defaultdict(list)
    for e in wave_entries:
        by_file[e["source_file"]].append(e)

    # Limit to max_files (prioritize files with most entries)
    sorted_files = sorted(by_file.items(), key=lambda x: -len(x[1]))[:max_files]
    limited_by_file = dict(sorted_files)

    # Create manifest
    manifest = {
        "wave_name": wave_name,
        "directory_pattern": dir_pattern,
        "total_entries": sum(len(entries) for entries in limited_by_file.values()),
        "total_files": len(limited_by_file),
        "max_files_limit": max_files,
        "files": [
            {
                "path": fpath,
                "entry_count": len(entries_list),
                "entries": entries_list,
            }
            for fpath, entries_list in sorted_files
        ],
    }

    WAVE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = WAVE_OUTPUT_DIR / f"{wave_name}_{dir_pattern.replace('/', '_')}.json"
    out_path.write_text(json.dumps(manifest, indent=2))

    print(f"Wave manifest: {out_path}")
    print(f"  Total entries (limited): {manifest['total_entries']}")
    print(f"  Total files (limited): {manifest['total_files']}")
    print(f"  Original total entries: {len(wave_entries)}")
    print(f"  Original total files: {len(by_file)}")
    print("\nTop 10 files by entry count:")
    for fpath, entries_list in sorted_files[:10]:
        print(f"  {len(entries_list):>3}  {fpath}")


if __name__ == "__main__":
    main()
