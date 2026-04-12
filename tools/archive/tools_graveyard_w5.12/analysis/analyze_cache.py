#!/usr/bin/env python3
"""Analyze cache contents to understand why it's incomplete"""

import json
from pathlib import Path


def analyze_cache():
    cache_path = Path("artifacts/adg/scan_result_cache.json")
    if not cache_path.exists():
        print("❌ Cache file does not exist")
        return

    cache = json.loads(cache_path.read_text())
    entries = cache.get("entries", {})

    print("📊 Cache Analysis:")
    print(f"   Total entries: {len(entries)}")
    print(f"   Cache size: {cache_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Show sample cached files
    print("\n📁 Sample cached files:")
    for i, (file_path, entry) in enumerate(list(entries.items())[:10]):
        print(f"   {i + 1}. {file_path}")
        print(f"      Hash: {entry['file_hash'][:16]}...")
        print(f"      Edges: {len(entry['edges'])}")

    # Check file patterns
    print("\n🔍 File patterns in cache:")
    patterns = {}
    for file_path in entries.keys():
        parts = file_path.split("/")
        if len(parts) > 1:
            prefix = parts[0]
            patterns[prefix] = patterns.get(prefix, 0) + 1

    for prefix, count in sorted(patterns.items()):
        print(f"   {prefix}/: {count} files")

    # Check if this looks like a test run
    print("\n🧪 Cache Origin Analysis:")
    if len(entries) == 100:
        print("   ✅ This looks like a test run (exactly 100 files)")
        print("   ❌ This is NOT a full cache (should be 6,557 files)")
    elif len(entries) < 1000:
        print("   ❌ Incomplete cache - likely from interrupted run")
    else:
        print("   ✅ Appears to be a full cache")

    # Estimate full cache size
    if len(entries) > 0:
        avg_entry_size = cache_path.stat().st_size / len(entries)
        estimated_full_size = avg_entry_size * 6557 / 1024 / 1024
        print("\n💾 Full Cache Estimate:")
        print(f"   Average entry size: {avg_entry_size / 1024:.1f} KB")
        print(f"   Estimated full cache size: {estimated_full_size:.1f} MB")


if __name__ == "__main__":
    analyze_cache()
