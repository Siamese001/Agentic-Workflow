#!/usr/bin/env python3
"""
Call-Site Mapper for AST + Fuzzy Definitions (Phase 1)

Maps discovered definitions to their call-sites within SSOT-approved folders.
Uses ripgrep-style word-boundary matching for deterministic results.

Usage:
    python tools/tmp_ok/callsite_mapper.py --inventory docs/reports/sub/ast_fuzzy_inventory.json --roots agentic_core tools ops_scripts --out-json docs/reports/sub/ast_fuzzy_callsites.json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_inventory(json_path: str) -> dict[str, Any]:
    """Load inventory JSON."""
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)

def extract_symbol_names(inventory: dict[str, Any]) -> set[str]:
    """Extract all unique symbol names from inventory."""
    symbols = set()
    for file_data in inventory.get("files", []):
        for candidate in file_data.get("candidates", []):
            symbols.add(candidate["name"])
    return symbols

def should_exclude(file_path: Path, excluded_patterns: list[str]) -> bool:
    """Check if file should be excluded."""
    path_str = str(file_path).replace("\\", "/")
    for pattern in excluded_patterns:
        if pattern in path_str:
            return True
    return False

def find_symbol_references(symbol: str, roots: list[str], excluded_patterns: list[str]) -> list[dict[str, Any]]:
    """Find all references to a symbol in the given roots."""
    references = []

    # Word boundary pattern for the symbol
    pattern = re.compile(r'\b' + re.escape(symbol) + r'\b')

    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue

        for py_file in sorted(root_path.rglob("*.py")):
            if should_exclude(py_file, excluded_patterns):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for match in pattern.finditer(line):
                        # Extract snippet (trim to reasonable length)
                        snippet = line.strip()
                        if len(snippet) > 100:
                            snippet = snippet[:97] + "..."

                        references.append({
                            "file": str(py_file).replace("\\", "/"),
                            "line": line_num,
                            "snippet": snippet
                        })
            except Exception:
                pass

    return references

def build_callsite_map(inventory: dict[str, Any], roots: list[str]) -> dict[str, Any]:
    """Build comprehensive call-site map for all discovered symbols."""

    excluded_patterns = ["tests", "apps_lic", "apps_rg", "apps_shared", "archives", ".backup", "__pycache__"]

    # Extract all symbol definitions
    definitions_by_symbol = defaultdict(list)
    for file_data in inventory.get("files", []):
        file_path = file_data["path"]
        for candidate in file_data.get("candidates", []):
            symbol = candidate["name"]
            definitions_by_symbol[symbol].append({
                "file": file_path,
                "line": candidate["line"],
                "kind": candidate["kind"]
            })

    # For each symbol, find all references
    callsite_map = {}
    symbol_ref_counts = {}

    for symbol in sorted(definitions_by_symbol.keys()):
        references = find_symbol_references(symbol, roots, excluded_patterns)

        # Filter out definition lines (they're not call-sites)
        definition_lines = {(d["file"], d["line"]) for d in definitions_by_symbol[symbol]}
        call_references = [
            ref for ref in references
            if (ref["file"], ref["line"]) not in definition_lines
        ]

        if call_references:
            callsite_map[symbol] = {
                "definitions": sorted(definitions_by_symbol[symbol], key=lambda x: (x["file"], x["line"])),
                "references": sorted(call_references, key=lambda x: (x["file"], x["line"])),
                "reference_count": len(call_references),
                "cross_root_usage": len(set(ref["file"].split('/')[0] for ref in call_references))
            }
            symbol_ref_counts[symbol] = len(call_references)

    # Identify central candidates (top by reference count)
    top_symbols = sorted(symbol_ref_counts.items(), key=lambda x: -x[1])[:20]

    central_candidates = []
    for symbol, ref_count in top_symbols:
        if ref_count > 0:
            cross_root = callsite_map[symbol]["cross_root_usage"]
            central_candidates.append({
                "symbol": symbol,
                "reference_count": ref_count,
                "cross_root_usage": cross_root,
                "justification": f"High inbound refs ({ref_count}) across {cross_root} root(s)"
            })

    return {
        "callsite_map": callsite_map,
        "central_candidates": central_candidates[:10],
        "summary": {
            "total_symbols": len(callsite_map),
            "symbols_with_references": len([s for s in callsite_map.values() if s["reference_count"] > 0]),
            "total_references": sum(s["reference_count"] for s in callsite_map.values())
        }
    }

def main():
    parser = argparse.ArgumentParser(
        description="Map call-sites for discovered AST and fuzzy definitions"
    )
    parser.add_argument("--inventory", required=True,
                       help="Path to inventory JSON file")
    parser.add_argument("--roots", nargs="+", required=True,
                       help="Root directories to scan for references")
    parser.add_argument("--out-json", required=True,
                       help="Output JSON file path")

    args = parser.parse_args()

    print(f"Loading inventory from: {args.inventory}", file=sys.stderr)
    inventory = load_inventory(args.inventory)

    print(f"Building call-site map (scanning roots: {args.roots})...", file=sys.stderr)
    callsite_data = build_callsite_map(inventory, args.roots)

    # Write JSON
    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(callsite_data, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Call-site map written to: {out_path}", file=sys.stderr)
    print(f"Symbols mapped: {callsite_data['summary']['total_symbols']}, "
          f"With references: {callsite_data['summary']['symbols_with_references']}", file=sys.stderr)

if __name__ == "__main__":
    main()
