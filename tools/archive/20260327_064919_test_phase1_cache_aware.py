#!/usr/bin/env python3
"""Test Phase 1.3: cache-aware scan mode selection."""

import json
import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def test_cache_aware_mode():
    """Test that cache-aware mode selection optimizes scanning based on cache state."""
    print("=== Phase 1.3: Cache-Aware Mode Test ===")
    print()

    # Create temporary directory for cache
    cache_dir = Path("test_cache")
    cache_dir.mkdir(exist_ok=True)

    try:
        # Test 1: No cache - should use full mode
        print("Test 1: No cache available")
        scanner_no_cache = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,
            cache_path=None,  # No cache
            scan_mode="auto"
        )

        # Force mode selection by calling scan (but we'll intercept the mode)
        scanner_no_cache.scan_mode = _get_cache_aware_scan_mode(
            None, Path("."), include_tests=False
        )

        print(f"  Selected mode: {scanner_no_cache.scan_mode}")
        print("  Expected: full")
        print(f"  Result: {'✓' if scanner_no_cache.scan_mode == 'full' else '✗'}")
        print()

        # Test 2: Build cache first
        print("Test 2: Building cache...")
        cache_file = cache_dir / "cache.json"
        scanner_build = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,
            cache_path=cache_file,
            scan_mode="full"
        )

        start_time = time.time()
        result_build = scanner_build.scan(commit_sha="build-cache")
        build_time = time.time() - start_time

        print(f"  Cache built in {build_time:.2f} seconds")
        print(f"  Cache file exists: {cache_file.exists()}")
        print()

        # Test 3: High cache hit rate - should use selective mode
        print("Test 3: High cache hit rate (production only)")
        scanner_high_cache = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,
            cache_path=cache_file,
            scan_mode="auto"
        )

        start_time = time.time()
        result_high_cache = scanner_high_cache.scan(commit_sha="high-cache")
        high_cache_time = time.time() - start_time

        print(f"  Scan time: {high_cache_time:.2f} seconds")
        print(f"  Selected mode: {scanner_high_cache.scan_mode}")
        print(f"  Total edges: {len(result_high_cache.edges)}")
        print()

        # Test 4: Tests included - should use structural_only
        print("Test 4: High cache hit rate (with tests)")
        scanner_tests = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=True,
            cache_path=cache_file,
            scan_mode="auto"
        )

        start_time = time.time()
        result_tests = scanner_tests.scan(commit_sha="with-tests")
        tests_time = time.time() - start_time

        print(f"  Scan time: {tests_time:.2f} seconds")
        print(f"  Selected mode: {scanner_tests.scan_mode}")
        print(f"  Total edges: {len(result_tests.edges)}")
        print()

        # Test 5: Cache analysis validation
        print("Test 5: Cache analysis validation")
        if cache_file.exists():
            with open(cache_file) as f:
                cache_data = json.load(f)

            cache_stats = cache_data.get("stats", {})
            hit_rate = cache_stats.get("hit_rate", 0.0)
            total_entries = cache_stats.get("hits", 0) + cache_stats.get("misses", 0)

            print(f"  Cache hit rate: {hit_rate:.2f}")
            print(f"  Total entries: {total_entries}")
            print(f"  Production mode: {'selective' if hit_rate > 0.7 else 'full'}")
            print(f"  Tests mode: {'structural_only' if hit_rate > 0.9 else 'selective' if hit_rate > 0.7 else 'full'}")
            print()

        # Analysis
        print("=== Analysis ===")

        # Verify mode selection logic
        expected_prod_mode = "selective" if cache_stats.get("hit_rate", 0) > 0.7 else "full"
        expected_test_mode = "structural_only" if cache_stats.get("hit_rate", 0) > 0.9 else "selective" if cache_stats.get("hit_rate", 0) > 0.7 else "full"

        prod_mode_correct = scanner_high_cache.scan_mode == expected_prod_mode
        test_mode_correct = scanner_tests.scan_mode == expected_test_mode

        print(f"Production mode selection: {'✓' if prod_mode_correct else '✗'}")
        print(f"Test mode selection: {'✓' if test_mode_correct else '✗'}")

        # Performance comparison
        if build_time > 0 and high_cache_time > 0:
            cache_speedup = build_time / high_cache_time
            print(f"Cache speedup: {cache_speedup:.1f}x")

        return {
            "no_cache_mode": scanner_no_cache.scan_mode,
            "prod_mode": scanner_high_cache.scan_mode,
            "test_mode": scanner_tests.scan_mode,
            "cache_hit_rate": cache_stats.get("hit_rate", 0),
            "cache_speedup": cache_speedup if build_time > 0 else 0,
            "prod_mode_correct": prod_mode_correct,
            "test_mode_correct": test_mode_correct
        }

    finally:
        # Cleanup
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

# Import the function for testing
from agentic_core.adg.extraction.static_scanner import _get_cache_aware_scan_mode

if __name__ == "__main__":
    results = test_cache_aware_mode()
    print("\n=== Phase 1.3 Test Complete ===")
    print(f"No cache mode: {results['no_cache_mode']}")
    print(f"Production mode: {results['prod_mode']}")
    print(f"Test mode: {results['test_mode']}")
    print(f"Cache hit rate: {results['cache_hit_rate']:.2f}")
    print(f"Cache speedup: {results['cache_speedup']:.1f}x")
    print(f"Mode selection correct: {'✓' if results['prod_mode_correct'] and results['test_mode_correct'] else '✗'}")
