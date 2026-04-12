#!/usr/bin/env python3
"""Compare two ADG artifacts to understand the 34% size reduction."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def analyze_structure(data: dict, label: str) -> None:
    """Analyze the structure of an ADG artifact."""
    print(f"\n{label} structure:")
    print(f"  Top-level keys: {list(data.keys())}")

    if "meta" in data:
        meta = data["meta"]
        print(f"  Built at: {meta.get('built_at', '?')}")
        print(f"  Scan roots: {meta.get('scan_roots', [])}")

    if "stats" in data:
        stats = data["stats"]
        print("  Stats:")
        for k, v in stats.items():
            print(f"    {k}: {v}")

    if "nodes" in data:
        nodes = data["nodes"]
        print(f"  Nodes: {len(nodes)} entries")
        if nodes:
            sample = list(nodes.items())[:3]
            print(f"    Sample keys: {[k for k, _ in sample]}")

    if "edges" in data:
        edges = data["edges"]
        if isinstance(edges, dict):
            print(f"  Edges: {len(edges)} source nodes")
            if edges:
                sample_src = list(edges.keys())[0]
                sample_targets = edges[sample_src]
                print(
                    f"    Sample: {sample_src} -> {len(sample_targets) if isinstance(sample_targets, list) else 1} targets"
                )
        elif isinstance(edges, list):
            print(f"  Edges: {len(edges)} edge records")

    if "syntax_errors" in data:
        errors = data["syntax_errors"]
        print(f"  Syntax errors: {len(errors)}")

    if "layer_violations" in data:
        violations = data["layer_violations"]
        print(f"  Layer violations: {len(violations)}")


def main() -> None:
    old_path = REPO / "artifacts" / "adg" / "adg_full_20260310T181458Z.json"
    new_path = REPO / "artifacts" / "adg" / "adg_full_20260310T232923Z.json"

    if not old_path.exists():
        print(f"Old file not found: {old_path}")
        return
    if not new_path.exists():
        print(f"New file not found: {new_path}")
        return

    old_size = old_path.stat().st_size
    new_size = new_path.stat().st_size
    reduction = (old_size - new_size) / old_size * 100

    print("=" * 70)
    print("ADG Artifact Size Comparison")
    print("=" * 70)
    print()
    print(f"Old: {old_path.name}")
    print(f"  Size: {old_size:,} bytes ({old_size / 1024 / 1024:.1f} MB)")
    print()
    print(f"New: {new_path.name}")
    print(f"  Size: {new_size:,} bytes ({new_size / 1024 / 1024:.1f} MB)")
    print()
    print(f"Reduction: {reduction:.1f}% ({(old_size - new_size) / 1024 / 1024:.1f} MB smaller)")

    # Load and analyze
    print("\nLoading artifacts...")
    old_data = json.loads(old_path.read_text(encoding="utf-8"))
    new_data = json.loads(new_path.read_text(encoding="utf-8"))

    analyze_structure(old_data, "OLD")
    analyze_structure(new_data, "NEW")

    # Compare specific metrics
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    old_stats = old_data.get("stats", {})
    new_stats = new_data.get("stats", {})

    metrics = [
        "total_nodes",
        "total_edges",
        "syntax_error_count",
        "layer_violation_count",
        "orphan_count",
    ]

    for metric in metrics:
        old_val = old_stats.get(metric, 0)
        new_val = new_stats.get(metric, 0)
        delta = new_val - old_val
        if old_val > 0:
            pct = (delta / old_val) * 100
            print(f"{metric}: {old_val} -> {new_val} ({delta:+d}, {pct:+.1f}%)")
        else:
            print(f"{metric}: {old_val} -> {new_val} ({delta:+d})")

    # Check for structural differences
    print("\nStructural changes:")
    old_keys = set(old_data.keys())
    new_keys = set(new_data.keys())

    removed = old_keys - new_keys
    added = new_keys - old_keys

    if removed:
        print(f"  Removed keys: {removed}")
    if added:
        print(f"  Added keys: {added}")
    if not removed and not added:
        print(f"  Same top-level keys: {sorted(old_keys)}")

    # Hypothesis
    print("\n" + "=" * 70)
    print("HYPOTHESIS")
    print("=" * 70)
    print()

    if old_stats.get("syntax_error_count", 0) > new_stats.get("syntax_error_count", 0):
        print("✓ Syntax errors reduced (files now parseable)")
        print("  → Fewer unparseable nodes = smaller artifact")

    if old_stats.get("orphan_count", 0) > new_stats.get("orphan_count", 0):
        print("✓ Orphan nodes reduced (better connectivity)")
        print("  → More nodes integrated into graph")

    if old_stats.get("total_edges", 0) < new_stats.get("total_edges", 0):
        print("✓ More edges (better import resolution)")
        print("  → But edges are smaller than node metadata")

    print("\nLikely cause: Corruption fixes removed malformed import statements")
    print("that were inflating the artifact with error metadata and orphan nodes.")


if __name__ == "__main__":
    main()
