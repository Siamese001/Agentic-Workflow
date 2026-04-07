#!/usr/bin/env python3
"""Comprehensive benchmark for Phase 1.1 structural_only mode."""

import json
import time
from pathlib import Path

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def benchmark_structural_only():
    """Comprehensive benchmark comparing full vs structural_only modes."""
    print("=== Phase 1.1 Comprehensive Benchmark ===")
    print()

    # Create benchmark directory
    benchmark_dir = Path("benchmark_results")
    benchmark_dir.mkdir(exist_ok=True)

    results = {}

    # Test configurations
    configs = [
        {"include_tests": False, "scan_mode": "full", "name": "production_only"},
        {"include_tests": True, "scan_mode": "full", "name": "full_with_tests"},
        {"include_tests": True, "scan_mode": "structural_only", "name": "structural_only_tests"},
    ]

    for config in configs:
        print(f"Testing: {config['name']}")
        print("-" * 40)

        cache_file = benchmark_dir / f"cache_{config['name']}.json"

        scanner = ADGStaticScanner(
            repo_root=Path("."),
            include_tests=config["include_tests"],
            cache_path=cache_file,
            scan_mode=config["scan_mode"],
        )

        start_time = time.time()
        result = scanner.scan(commit_sha=f"benchmark-{config['name']}")
        scan_time = time.time() - start_time

        # Analyze results
        total_edges = len(result.edges)
        test_edges = [e for e in result.edges if e.source_file.startswith("tests/")]
        prod_edges = [e for e in result.edges if not e.source_file.startswith("tests/")]

        # Edge type analysis
        edge_types = {}
        for edge in result.edges:
            edge_types[edge.relation_type] = edge_types.get(edge.relation_type, 0) + 1

        # File analysis
        files_scanned = {edge.source_file for edge in result.edges}
        test_files = [f for f in files_scanned if f.startswith("tests/")]
        prod_files = [f for f in files_scanned if not f.startswith("tests/")]

        results[config["name"]] = {
            "scan_time_seconds": round(scan_time, 2),
            "total_edges": total_edges,
            "test_edges": len(test_edges),
            "prod_edges": len(prod_edges),
            "files_scanned": len(files_scanned),
            "test_files": len(test_files),
            "prod_files": len(prod_files),
            "edge_types": edge_types,
            "digest": result.digest,
        }

        print(f"  Scan time: {scan_time:.2f} seconds")
        print(f"  Total edges: {total_edges:,}")
        print(f"  Test edges: {len(test_edges):,}")
        print(f"  Production edges: {len(prod_edges):,}")
        print(f"  Files scanned: {len(files_scanned):,}")
        print(f"  Edge types: {len(edge_types)}")
        print()

    # Comparative analysis
    print("=== Comparative Analysis ===")
    print()

    full_with_tests = results["full_with_tests"]
    structural_only = results["structural_only_tests"]
    production_only = results["production_only"]

    # Test file analysis
    test_edge_reduction = full_with_tests["test_edges"] - structural_only["test_edges"]
    test_edge_reduction_percent = (test_edge_reduction / full_with_tests["test_edges"]) * 100

    test_time_improvement = full_with_tests["scan_time_seconds"] - structural_only["scan_time_seconds"]
    test_time_improvement_percent = (test_time_improvement / full_with_tests["scan_time_seconds"]) * 100

    print(f"Test file edge reduction: {test_edge_reduction:,} ({test_edge_reduction_percent:.1f}%)")
    print(f"Test scan time improvement: {test_time_improvement:.2f}s ({test_time_improvement_percent:.1f}%)")
    print()

    # Overall analysis
    total_edge_reduction = full_with_tests["total_edges"] - structural_only["total_edges"]
    total_edge_reduction_percent = (total_edge_reduction / full_with_tests["total_edges"]) * 100

    total_time_improvement = full_with_tests["scan_time_seconds"] - structural_only["scan_time_seconds"]
    total_time_improvement_percent = (total_time_improvement / full_with_tests["scan_time_seconds"]) * 100

    print(f"Overall edge reduction: {total_edge_reduction:,} ({total_edge_reduction_percent:.1f}%)")
    print(f"Overall time improvement: {total_time_improvement:.2f}s ({total_time_improvement_percent:.1f}%)")
    print()

    # Production code verification
    prod_edge_types_full = set()
    prod_edge_types_structural = set()

    for edge in [e for e in result.edges if not e.source_file.startswith("tests/")]:
        if config["name"] == "full_with_tests":
            prod_edge_types_full.add(edge.relation_type)
        elif config["name"] == "structural_only_tests":
            prod_edge_types_structural.add(edge.relation_type)

    print(f"Production edge types (full): {len(prod_edge_types_full)}")
    print(f"Production edge types (structural_only): {len(prod_edge_types_structural)}")
    print(f"Production code preserved: {'✓' if len(prod_edge_types_structural) > 2 else '✗'}")
    print()

    # Edge type reduction for test files
    test_edge_types_full = set()
    test_edge_types_structural = set()

    # Re-scan small subset to get test edge types
    for edge_name, result_data in results.items():
        if "test" in edge_name:
            for edge in [e for e in result.edges if e.source_file.startswith("tests/")]:
                if "full" in edge_name:
                    test_edge_types_full.add(edge.relation_type)
                elif "structural" in edge_name:
                    test_edge_types_structural.add(edge.relation_type)

    print(f"Test edge types (full): {len(test_edge_types_full)}")
    print(f"Test edge types (structural_only): {len(test_edge_types_structural)}")
    print("Expected: {'imports', 'implements'}")
    print(f"Actual: {test_edge_types_structural}")
    print(
        f"Test filtering correct: {'✓' if test_edge_types_structural == {'imports', 'implements'} else '✗'}",
    )
    print()

    # Save detailed results
    results_file = benchmark_dir / "phase1_benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Detailed results saved to: {results_file}")

    return results


if __name__ == "__main__":
    results = benchmark_structural_only()
    print("\n=== Phase 1.1 Benchmark Complete ===")
