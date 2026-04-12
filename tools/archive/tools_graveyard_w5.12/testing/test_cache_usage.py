#!/usr/bin/env python3
"""Test if cache is being used properly"""

import time
from pathlib import Path


def test_cache_usage():
    """Test cache usage with existing cache file"""
    print("=== Cache Usage Test ===")

    cache_file = Path("artifacts/adg/scan_result_cache.json")
    print(f"Cache file exists: {cache_file.exists()}")
    print(f"Cache file size: {cache_file.stat().st_size / 1024 / 1024:.1f} MB")

    # Test with cache
    print("\n1. Testing with existing cache...")
    start = time.time()

    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner(
        repo_root=Path("C:/Git/Agentic-Workflow"),
        cache_path=cache_file,
    )

    # Test just the first 50 files to see cache behavior
    import agentic_core.adg.extraction.static_scanner as scanner_module

    original_iter = scanner_module._iter_python_files

    def limited_iter(root):
        for i, f in enumerate(original_iter(root)):
            if i >= 50:
                break
            yield f

    scanner_module._iter_python_files = limited_iter

    try:
        result = scanner.scan()
        duration = time.time() - start

        print(f"✅ Limited scan (50 files) completed in {duration:.2f}s")
        print(f"   Modules: {len(result.modules)}")
        print(f"   Edges: {len(result.edges)}")
        print(f"   Cache hits: {result.manifest.cache_hits}")
        print(f"   Cache misses: {result.manifest.cache_misses}")
        print(f"   Cache hit rate: {result.manifest.cache_hit_rate:.1%}")

        if result.manifest.cache_hit_rate > 0:
            print("✅ Cache is working!")
        else:
            print("❌ Cache not being used")

    finally:
        # Restore original function
        scanner_module._iter_python_files = original_iter


if __name__ == "__main__":
    test_cache_usage()
