#!/usr/bin/env python3
"""Check cache file structure"""

import json
from pathlib import Path

cache_path = Path("artifacts/adg/scan_result_cache.json")
if not cache_path.exists():
    print("Cache file does not exist")
else:
    cache = json.loads(cache_path.read_text())
    print(f"Cache file size: {cache_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Cache keys: {list(cache.keys())}")
    print(f"Cache version: {cache.get('version')}")
    print(f"Cache entries: {len(cache.get('entries', {}))}")
    print(f"Has _cache_key: {'_cache_key' in cache}")

    # Check if this is a ScanCache format or ScanResult format
    if "version" in cache and "entries" in cache:
        print("\n✅ This is a ScanCache format (used by scanner)")
        print("   - Used by ADGStaticScanner.scan()")
        print("   - Contains per-file cached edges")
    elif "manifest" in cache or "edges" in cache:
        print("\n✅ This is a ScanResult format (used by cache_loader)")
        print("   - Used by load_or_scan()")
        print("   - Contains full scan result")
    else:
        print("\n❌ Unknown cache format")
