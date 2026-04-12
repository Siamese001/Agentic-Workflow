#!/usr/bin/env python3
"""Check archived ADG files to see what proper size should be"""

import gzip
import json
from pathlib import Path


def check_archived_adg():
    # Check a recent archived symbol graph
    archive_file = Path("artifacts/adg/_archive/2026-03/adg_symbol_graph_03162026_2024.json.gz")
    if archive_file.exists():
        with gzip.open(archive_file, "rt") as f:
            data = json.load(f)
        print("📊 Archived ADG Analysis (March 16, 2026):")
        print(f"   Compressed size: {archive_file.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"   Uncompressed size: {len(json.dumps(data)) / 1024 / 1024:.1f} MB")
        print(f"   Number of edges: {len(data.get('edges', [])):,}")
        print(f"   Number of nodes: {len(data.get('nodes', [])):,}")

        # Check current ADG
        current_file = Path("artifacts/adg/adg_symbol_graph_03222026_1351.json")
        if current_file.exists():
            current_data = json.loads(current_file.read_text())
            print("\n📊 Current ADG Analysis (March 22, 2026):")
            print(f"   File size: {current_file.stat().st_size / 1024:.1f} KB")
            print(f"   Number of edges: {len(current_data.get('edges', [])):,}")
            print(f"   Number of nodes: {len(current_data.get('nodes', [])):,}")

            print("\n🔍 Comparison:")
            print(
                f"   Edge ratio: {len(current_data.get('edges', [])) / len(data.get('edges', [])) * 100:.1f}%"
            )
            print(
                f"   Node ratio: {len(current_data.get('nodes', [])) / len(data.get('nodes', [])) * 100:.1f}%"
            )
        else:
            print("\n❌ Current ADG file not found")
    else:
        print("❌ Archive file not found")


if __name__ == "__main__":
    check_archived_adg()
