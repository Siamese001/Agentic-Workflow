#!/usr/bin/env python3
"""Test Phase 1.4: enhanced runtime-only edge filtering."""

import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def test_enhanced_filtering():
    """Test that enhanced runtime filtering optimizes edge removal."""
    print("=== Phase 1.4: Enhanced Runtime Filtering Test ===")
    print()

    # Create temporary directory for cache
    cache_dir = Path("test_cache")
    cache_dir.mkdir(exist_ok=True)

    try:
        # Test 1: Full mode with tests (baseline)
        print("Test 1: Full mode with tests (baseline)")
        scanner_full = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=True,
            cache_path=cache_dir / "full_cache.json",
            scan_mode="full",
        )

        start_time = time.time()
        result_full = scanner_full.scan(commit_sha="full-baseline")
        full_time = time.time() - start_time

        print(f"  Scan time: {full_time:.2f} seconds")
        print(f"  Total edges: {len(result_full.edges)}")
        print()

        # Test 2: Selective mode with enhanced filtering
        print("Test 2: Selective mode with enhanced filtering")
        scanner_selective = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=True,
            cache_path=cache_dir / "selective_cache.json",
            scan_mode="selective",
        )

        start_time = time.time()
        result_selective = scanner_selective.scan(commit_sha="selective-enhanced")
        selective_time = time.time() - start_time

        print(f"  Scan time: {selective_time:.2f} seconds")
        print(f"  Total edges: {len(result_selective.edges)}")
        print()

        # Test 3: Production only with enhanced filtering
        print("Test 3: Production only with enhanced filtering")
        scanner_prod = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=False,
            cache_path=cache_dir / "prod_cache.json",
            scan_mode="selective",
        )

        start_time = time.time()
        result_prod = scanner_prod.scan(commit_sha="prod-enhanced")
        prod_time = time.time() - start_time

        print(f"  Scan time: {prod_time:.2f} seconds")
        print(f"  Total edges: {len(result_prod.edges)}")
        print()

        # Analysis
        print("=== Analysis ===")

        # Edge type analysis
        def analyze_edges(edges, label):
            edge_types = {}
            runtime_edges = 0
            kept_runtime_edges = 0

            for edge in edges:
                edge_types[edge.relation_type] = edge_types.get(edge.relation_type, 0) + 1

                # Check if it's a runtime edge
                from agentic_core.adg.extraction.static_scanner import (
                    _is_runtime_only_relation,
                    _should_keep_runtime_edge,
                )
                if _is_runtime_only_relation(edge.relation_type):
                    runtime_edges += 1
                    if _should_keep_runtime_edge(edge):
                        kept_runtime_edges += 1

            print(f"{label}:")
            print(f"  Total edges: {len(edges)}")
            print(f"  Runtime edges: {runtime_edges}")
            print(f"  Kept runtime edges: {kept_runtime_edges}")
            print(f"  Filtered runtime edges: {runtime_edges - kept_runtime_edges}")
            print(f"  Runtime filtering rate: {((runtime_edges - kept_runtime_edges) / runtime_edges * 100) if runtime_edges > 0 else 0:.1f}%")
            print(f"  Edge types: {len(edge_types)}")

            return edge_types, runtime_edges, kept_runtime_edges

        full_types, full_runtime, full_kept = analyze_edges(result_full.edges, "Full mode")
        print()

        selective_types, selective_runtime, selective_kept = analyze_edges(result_selective.edges, "Selective mode")
        print()

        prod_types, prod_runtime, prod_kept = analyze_edges(result_prod.edges, "Production only")
        print()

        # Calculate improvements
        total_edge_reduction = len(result_full.edges) - len(result_selective.edges)
        total_reduction_percent = (total_edge_reduction / len(result_full.edges)) * 100 if result_full.edges else 0

        runtime_filtering_improvement = (full_runtime - selective_runtime) / full_runtime * 100 if full_runtime > 0 else 0

        print("=== Results ===")
        print(f"Total edge reduction: {total_edge_reduction} ({total_reduction_percent:.1f}%)")
        print(f"Runtime filtering improvement: {runtime_filtering_improvement:.1f}%")
        print(f"Scan time improvement: {full_time - selective_time:.2f} seconds")

        # Verify critical edges preserved
        critical_runtime_types = {
            "applies_guardrail", "verifies_policy", "validated_by_safety_plane",
            "execution_terminates_at_uwg", "records_execution_trace",
        }

        selective_critical = {rt for rt in selective_types.keys() if rt in critical_runtime_types}
        prod_critical = {rt for rt in prod_types.keys() if rt in critical_runtime_types}

        print(f"Critical runtime edges preserved (selective): {len(selective_critical)}/{len(critical_runtime_types)}")
        print(f"Critical runtime edges preserved (prod): {len(prod_critical)}/{len(critical_runtime_types)}")

        if selective_critical == critical_runtime_types:
            print("✓ All critical runtime edges preserved in selective mode")
        else:
            missing = critical_runtime_types - selective_critical
            print(f"✗ Missing critical runtime edges: {missing}")

        return {
            "full_edges": len(result_full.edges),
            "selective_edges": len(result_selective.edges),
            "prod_edges": len(result_prod.edges),
            "total_reduction_percent": total_reduction_percent,
            "runtime_filtering_improvement": runtime_filtering_improvement,
            "time_improvement": full_time - selective_time,
            "critical_preserved": len(selective_critical) == len(critical_runtime_types),
        }

    finally:
        # Cleanup
        import shutil
        if cache_dir.exists():
            shutil.rmtree(cache_dir)

if __name__ == "__main__":
    results = test_enhanced_filtering()
    print("\n=== Phase 1.4 Test Complete ===")
    print(f"Total edge reduction: {results['total_reduction_percent']:.1f}%")
    print(f"Runtime filtering improvement: {results['runtime_filtering_improvement']:.1f}%")
    print(f"Time improvement: {results['time_improvement']:.2f} seconds")
    print(f"Critical edges preserved: {'✓' if results['critical_preserved'] else '✗'}")
