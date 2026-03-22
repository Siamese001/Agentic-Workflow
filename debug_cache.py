#!/usr/bin/env python3
"""Debug scan cache behavior"""

import time
import os
from pathlib import Path

def debug_cache_behavior():
    """Debug why scan cache disappears"""
    artifacts_dir = Path("artifacts/adg")
    cache_file = artifacts_dir / "scan_result_cache.json"
    
    print("=== Scan Cache Debug ===")
    
    # Check initial state
    print(f"\n1. Initial state:")
    print(f"   Cache exists: {cache_file.exists()}")
    if cache_file.exists():
        print(f"   Cache size: {cache_file.stat().st_size / 1024:.1f} KB")
        print(f"   Cache mtime: {time.ctime(cache_file.stat().st_mtime)}")
    
    # Run a quick ADG scan to create cache
    print(f"\n2. Running ADG generation to create cache...")
    os.system("python tools/generate_full_adg.py")
    
    # Check after generation
    print(f"\n3. After ADG generation:")
    print(f"   Cache exists: {cache_file.exists()}")
    if cache_file.exists():
        print(f"   Cache size: {cache_file.stat().st_size / 1024:.1f} KB")
        print(f"   Cache mtime: {time.ctime(cache_file.stat().st_mtime)}")
    
    # Wait a moment and check again
    time.sleep(2)
    print(f"\n4. After 2 second delay:")
    print(f"   Cache exists: {cache_file.exists()}")
    if cache_file.exists():
        print(f"   Cache size: {cache_file.stat().st_size / 1024:.1f} KB")
        print(f"   Cache mtime: {time.ctime(cache_file.stat().st_mtime)}")
    
    # List all files in artifacts directory
    print(f"\n5. All files in artifacts/adg/:")
    for f in sorted(artifacts_dir.glob("*")):
        if f.is_file():
            print(f"   {f.name:<40} {f.stat().st_size / 1024:>6.1f} KB")

if __name__ == "__main__":
    debug_cache_behavior()
