#!/usr/bin/env python3
"""Performance test to identify bottlenecks"""

import time
from pathlib import Path


def test_scan_performance():
    """Test individual components for performance bottlenecks"""
    print("=== Performance Analysis ===")

    # Test file discovery
    print("\n1. Testing file discovery...")
    start = time.time()
    from agentic_core.adg.extraction.static_scanner import _iter_python_files

    files = list(_iter_python_files(Path("C:/Git/Agentic-Workflow")))
    discovery_time = time.time() - start
    print(f"   Found {len(files)} files in {discovery_time:.2f}s")

    # Test single file scan (different types)
    print("\n2. Testing single file scan performance...")
    from agentic_core.adg.extraction.static_scanner import _scan_file

    test_files = [
        files[0],  # First file
        files[len(files) // 2],  # Middle file
        files[-1],  # Last file
    ]

    for i, test_file in enumerate(test_files):
        start = time.time()
        edges, had_error = _scan_file(test_file, Path("C:/Git/Agentic-Workflow"), True)
        scan_time = time.time() - start
        print(f"   File {i + 1}: {test_file.name}")
        print(f"     Edges: {len(edges)}, Error: {had_error}, Time: {scan_time:.3f}s")

    # Test cache operations
    print("\n3. Testing cache operations...")
    from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

    cache = ScanCache()
    test_file = files[0]

    # Test file hashing
    start = time.time()
    fhash = file_hash(test_file)
    hash_time = time.time() - start
    print(f"   File hash: {hash_time:.4f}s")

    # Test cache put/get
    start = time.time()
    cache.put("test_key", fhash, [])
    put_time = time.time() - start
    print(f"   Cache put: {put_time:.4f}s")

    start = time.time()
    cached_edges, hit = cache.get("test_key", fhash)
    get_time = time.time() - start
    print(f"   Cache get: {get_time:.4f}s (hit: {hit})")

    # Estimate full scan time
    avg_scan_time = 0.96  # From previous test (100 files in 96s)
    estimated_full_time = avg_scan_time * len(files)
    print("\n4. Performance Estimates:")
    print(f"   Average per file: {avg_scan_time:.3f}s")
    print(f"   Estimated full scan: {estimated_full_time / 60:.1f} minutes")
    print(f"   Files to process: {len(files)}")

    # Check if cache would help
    print("\n5. Cache Impact Analysis:")
    print("   With 100% cache hit rate: ~30 seconds (cache loading)")
    print(f"   With 0% cache hit rate: {estimated_full_time / 60:.1f} minutes")
    print(f"   Current cache file exists: {Path('artifacts/adg/scan_result_cache.json').exists()}")


if __name__ == "__main__":
    test_scan_performance()
