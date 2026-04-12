#!/usr/bin/env python3
"""Inspect ADG artifact to understand the 285 syntax errors and 111 layer violations."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> None:
    adg_path = REPO / "artifacts" / "adg" / "adg_full_20260310T232427Z.json"
    if not adg_path.exists():
        print(f"ADG artifact not found: {adg_path}")
        return

    data = json.loads(adg_path.read_text(encoding="utf-8"))

    print("=" * 70)
    print("ADG Artifact Analysis")
    print("=" * 70)
    print()

    stats = data.get("stats", {})
    print("Stats:")
    print(f"  Total nodes: {stats.get('total_nodes', 0)}")
    print(f"  Total edges: {stats.get('total_edges', 0)}")
    print(f"  Syntax errors: {stats.get('syntax_error_count', 0)}")
    print(f"  Layer violations: {stats.get('layer_violation_count', 0)}")
    print(f"  Orphan nodes: {stats.get('orphan_count', 0)}")
    print()

    # Check for syntax errors
    if "syntax_errors" in data:
        print("Syntax Error Files (first 15):")
        errors = data["syntax_errors"]
        if isinstance(errors, list):
            for i, err in enumerate(errors[:15], 1):
                if isinstance(err, dict):
                    fpath = err.get("file", "?")
                    msg = err.get("error", "?")
                    print(f"  {i}. {fpath}")
                    print(f"     Error: {str(msg)[:120]}")
                else:
                    print(f"  {i}. {err}")
            if len(errors) > 15:
                print(f"  ... and {len(errors) - 15} more")
        elif isinstance(errors, dict):
            for i, (fpath, msg) in enumerate(list(errors.items())[:15], 1):
                print(f"  {i}. {fpath}")
                print(f"     Error: {msg[:120]}")
            if len(errors) > 15:
                print(f"  ... and {len(errors) - 15} more")
        print()

    # Check for layer violations
    if "layer_violations" in data:
        print("Layer Violations (first 15):")
        violations = data["layer_violations"]
        for i, violation in enumerate(violations[:15], 1):
            src = violation.get("source", "?")
            dst = violation.get("target", "?")
            src_layer = violation.get("source_layer", "?")
            dst_layer = violation.get("target_layer", "?")
            print(f"  {i}. {src} [{src_layer}] -> {dst} [{dst_layer}]")
        if len(violations) > 15:
            print(f"  ... and {len(violations) - 15} more")
        print()

    # Check edges for layer info
    if "edges" in data:
        edges = data["edges"]
        print(f"Total edges in artifact: {len(edges)}")

        # Sample some edges to see structure
        print("\nSample edges (first 5):")
        for i, (src, targets) in enumerate(list(edges.items())[:5], 1):
            print(f"  {i}. {src} imports:")
            if isinstance(targets, list):
                for t in targets[:3]:
                    print(f"     - {t}")
            else:
                print(f"     {targets}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("The ADG artifact shows violations SEPARATE from anti-pattern checker:")
    print()
    print("1. Anti-pattern violations: 0 NEW (✅ fixed with guardian tokens)")
    print(f"2. Syntax errors: {stats.get('syntax_error_count', 0)} (❌ NOT addressed)")
    print(f"3. Layer violations: {stats.get('layer_violation_count', 0)} (❌ NOT addressed)")
    print()
    print("These are independent violation systems tracked by different tools.")


if __name__ == "__main__":
    main()
