#!/usr/bin/env python3
"""Test Phase 1.1: structural_only scan mode for test files."""

import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def test_structural_only_mode():
    """Test that structural_only mode reduces edge count for test files."""
    print("=== Phase 1.1: Structural-Only Mode Test ===")
    print()

    # Test on a small subset for speed
    test_files = [
        "tests/unit_min_deps/test_vllm_replay.py",
        "tests/unit_min_deps/test_version_store.py",
    ]

    # Create temporary directory for cache
    cache_dir = Path("test_cache")
    cache_dir.mkdir(exist_ok=True)

    try:
        # Test 1: Full mode on test files
        print("Test 1: Full scan mode on test files")
        scanner_full = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=True,
            cache_path=cache_dir / "full_cache.json",
            scan_mode="full",
        )

        start_time = time.time()
        result_full = scanner_full.scan(commit_sha="test-full")
        full_time = time.time() - start_time

        # Filter to only test file edges
        test_edges_full = [e for e in result_full.edges if e.source_file.startswith("tests/")]

        print(f"  Scan time: {full_time:.2f} seconds")
        print(f"  Total edges: {len(result_full.edges)}")
        print(f"  Test file edges: {len(test_edges_full)}")
        print(f"  Digest: {result_full.digest[:16]}...")
        print()

        # Test 2: Structural-only mode on test files
        print("Test 2: Structural-only scan mode on test files")
        scanner_structural = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=True,
            cache_path=cache_dir / "structural_cache.json",
            scan_mode="structural_only",
        )

        start_time = time.time()
        result_structural = scanner_structural.scan(commit_sha="test-structural")
        structural_time = time.time() - start_time

        # Filter to only test file edges
        test_edges_structural = [e for e in result_structural.edges if e.source_file.startswith("tests/")]

        print(f"  Scan time: {structural_time:.2f} seconds")
        print(f"  Total edges: {len(result_structural.edges)}")
        print(f"  Test file edges: {len(test_edges_structural)}")
        print(f"  Digest: {result_structural.digest[:16]}...")
        print()

        # Test 3: Analysis
        print("=== Analysis ===")

        # Count edge types in test files for both modes
        edge_types_full = {}
        edge_types_structural = {}

        for edge in test_edges_full:
            edge_types_full[edge.relation_type] = edge_types_full.get(edge.relation_type, 0) + 1

        for edge in test_edges_structural:
            edge_types_structural[edge.relation_type] = edge_types_structural.get(edge.relation_type, 0) + 1

        print("Test file edge types (full mode):")
        for rel_type, count in sorted(edge_types_full.items()):
            print(f"  {rel_type}: {count}")

        print("\nTest file edge types (structural_only mode):")
        for rel_type, count in sorted(edge_types_structural.items()):
            print(f"  {rel_type}: {count}")

        # Calculate reduction
        edge_reduction = len(test_edges_full) - len(test_edges_structural)
        reduction_percent = (edge_reduction / len(test_edges_full)) * 100 if test_edges_full else 0

        print("\n=== Results ===")
        print(f"Test file edges reduced: {edge_reduction} ({reduction_percent:.1f}%)")
        print(f"Scan time improvement: {full_time - structural_time:.2f} seconds")

        # Verify only imports and inheritance remain for test files
        expected_relations = {"imports", "implements"}
        actual_relations = set(edge_types_structural.keys())

        if expected_relations == actual_relations:
            print("✓ structural_only mode correctly limited to imports + inheritance")
        else:
            print(f"✗ Expected {expected_relations}, got {actual_relations}")

        # Verify production code still gets full treatment
        prod_edges_structural = [e for e in result_structural.edges if not e.source_file.startswith("tests/")]
        prod_relation_types = {e.relation_type for e in prod_edges_structural}

        if len(prod_relation_types) > 2:  # Should have many relation types for production
            print("✓ Production code still gets full scan treatment")
        else:
            print("✗ Production code may be incorrectly limited")

        return {
            "full_edges": len(test_edges_full),
            "structural_edges": len(test_edges_structural),
            "reduction_percent": reduction_percent,
            "time_improvement": full_time - structural_time,
        }

    finally:
        # Cleanup
        import shutil

        if cache_dir.exists():
            shutil.rmtree(cache_dir)


if __name__ == "__main__":
    results = test_structural_only_mode()
    print("\n=== Phase 1.1 Test Complete ===")
    print(f"Edge reduction: {results['reduction_percent']:.1f}%")
    print(f"Time improvement: {results['time_improvement']:.2f} seconds")
