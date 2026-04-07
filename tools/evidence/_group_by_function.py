"""Group narrows_possible entries by function for batch review.

Usage:
    python tools/evidence/_group_by_function.py <manifest_path>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python _group_by_function.py <manifest_path>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    manifest = json.loads(manifest_path.read_text())

    # Group by function name
    by_function = defaultdict(list)
    for file_data in manifest["files"]:
        for entry in file_data["entries"]:
            func_name = entry.get("containing_function") or "<module>"
            by_function[func_name].append({
                "file": file_data["path"],
                "line": entry["line_no"],
                "layer": entry["layer"],
            })

    # Sort by entry count (descending)
    sorted_funcs = sorted(by_function.items(), key=lambda x: -len(x[1]))

    print(f"Wave: {manifest['wave_name']}")
    print(f"Total entries: {manifest['total_entries']}")
    print(f"Total files: {manifest['total_files']}")
    print(f"Unique functions: {len(sorted_funcs)}")
    print("\n" + "=" * 80)
    print("GROUPED BY FUNCTION (sorted by entry count)")
    print("=" * 80 + "\n")

    for func_name, entries in sorted_funcs:
        print(f"Function: {func_name}")
        print(f"  Entry count: {len(entries)}")
        print(f"  Files: {len(set(e['file'] for e in entries))}")
        print(f"  Lines: {', '.join(str(e['line']) for e in entries[:10])}" +
              (f" ... ({len(entries) - 10} more)" if len(entries) > 10 else ""))
        print()


if __name__ == "__main__":
    main()
