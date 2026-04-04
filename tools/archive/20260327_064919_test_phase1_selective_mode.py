#!/usr/bin/env python3
"""Test Phase 1.2: selective scan mode for production code."""

import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def test_selective_mode():
    """Test that selective mode optimizes production code scanning."""
    print("=== Phase 1.2: Selective Mode Test ===")
    print()

    # Create temporary directory for cache
    cache_dir = Path("test_cache")
    cache_dir.mkdir(exist_ok=True)

    try:
        # Test 1: Full mode
        print("Test 1: Full scan mode")
        scanner_full = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,  # Production only for cleaner comparison
            cache_path=cache_dir / "full_cache.json",
            scan_mode="full"
        )

        start_time = time.time()
        result_full = scanner_full.scan(commit_sha="test-full")
        full_time = time.time() - start_time

        print(f"  Scan time: {full_time:.2f} seconds")
        print(f"  Total edges: {len(result_full.edges)}")
        print(f"  Files scanned: {len(set(edge.source_file for edge in result_full.edges))}")
        print()

        # Test 2: Selective mode
        print("Test 2: Selective scan mode")
        scanner_selective = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,
            cache_path=cache_dir / "selective_cache.json",
            scan_mode="selective"
        )

        start_time = time.time()
        result_selective = scanner_selective.scan(commit_sha="test-selective")
        selective_time = time.time() - start_time

        print(f"  Scan time: {selective_time:.2f} seconds")
        print(f"  Total edges: {len(result_selective.edges)}")
        print(f"  Files scanned: {len(set(edge.source_file for edge in result_selective.edges))}")
        print()

        # Analysis
        print("=== Analysis ===")

        # Edge type analysis
        edge_types_full = {}
        edge_types_selective = {}

        for edge in result_full.edges:
            edge_types_full[edge.relation_type] = edge_types_full.get(edge.relation_type, 0) + 1

        for edge in result_selective.edges:
            edge_types_selective[edge.relation_type] = edge_types_selective.get(edge.relation_type, 0) + 1

        print(f"Edge types (full mode): {len(edge_types_full)}")
        print(f"Edge types (selective mode): {len(edge_types_selective)}")
        print()

        # Calculate reduction
        edge_reduction = len(result_full.edges) - len(result_selective.edges)
        reduction_percent = (edge_reduction / len(result_full.edges)) * 100 if result_full.edges else 0
        time_improvement = full_time - selective_time

        print("=== Results ===")
        print(f"Edges reduced: {edge_reduction} ({reduction_percent:.1f}%)")
        print(f"Time improvement: {time_improvement:.2f} seconds")

        # Verify selective mode still captures key edge types
        expected_core_edges = {"imports", "implements"}
        actual_edges = set(edge_types_selective.keys())

        if expected_core_edges.issubset(actual_edges):
            print("✓ Core structural edges preserved")
        else:
            print(f"✗ Missing core edges: {expected_core_edges - actual_edges}")

        # Check for selective enhancement based on file types
        enhanced_visitors = set()
        for edge in result_selective.edges:
            if edge.relation_type in ["calls", "reads_from", "writes_to"]:
                enhanced_visitors.add(edge.relation_type)

        if enhanced_visitors:
            print(f"✓ Selective enhancement active: {enhanced_visitors}")
        else:
            print("✗ No selective enhancement detected")

        return {
            "full_edges": len(result_full.edges),
            "selective_edges": len(result_selective.edges),
            "reduction_percent": reduction_percent,
            "time_improvement": time_improvement,
            "edge_types_full": len(edge_types_full),
            "edge_types_selective": len(edge_types_selective)
        }

    finally:
        # Cleanup
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

if __name__ == "__main__":
    results = test_selective_mode()
    print("\n=== Phase 1.2 Test Complete ===")
    print(f"Edge reduction: {results['reduction_percent']:.1f}%")
    print(f"Time improvement: {results['time_improvement']:.2f} seconds")
    print(f"Edge types: {results['edge_types_full']} → {results['edge_types_selective']}")
