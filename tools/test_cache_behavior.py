#!/usr/bin/env python3
"""Test scan cache behavior"""

import sys
import time
from pathlib import Path

sys.path.append('tools')
from generate_full_adg import generate_full_adg


def test_cache_behavior():
    """Test if scan cache persists and accelerates refresh"""
    artifacts_dir = Path("artifacts/adg")
    cache_file = artifacts_dir / "scan_result_cache.json"

    print("=== Scan Cache Behavior Test ===")

    # First run - should create cache
    print("\n1. First ADG run (should create cache):")
    start = time.time()
    generate_full_adg(artifacts_dir, "test1", archive_old=False)
    first_duration = time.time() - start
    print(f"   Duration: {first_duration:.2f}s")
    print(f"   Cache exists: {cache_file.exists()}")
    if cache_file.exists():
        print(f"   Cache size: {cache_file.stat().st_size / 1024:.1f} KB")

    # Second run - should use cache
    print("\n2. Second ADG run (should use cache):")
    start = time.time()
    generate_full_adg(artifacts_dir, "test2", archive_old=False)
    second_duration = time.time() - start
    print(f"   Duration: {second_duration:.2f}s")
    print(f"   Cache exists: {cache_file.exists()}")
    if cache_file.exists():
        print(f"   Cache size: {cache_file.stat().st_size / 1024:.1f} KB")

    # Speedup analysis
    if second_duration > 0:
        speedup = first_duration / second_duration
        print(f"\n🎯 Cache speedup: {speedup:.2f}x")
        if speedup > 1.5:
            print("   ✅ Cache is providing significant acceleration")
        elif speedup > 1.1:
            print("   ⚠️  Cache providing modest acceleration")
        else:
            print("   ❌ Cache not providing expected acceleration")

if __name__ == "__main__":
    test_cache_behavior()
