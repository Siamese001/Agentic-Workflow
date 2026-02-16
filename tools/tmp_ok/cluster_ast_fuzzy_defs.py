#!/usr/bin/env python3
"""
AST + Fuzzy Near-Duplicate Clustering for SSOT Consolidation (Phase 1)

Analyzes discovered definitions to identify exact and near-duplicate clusters.
Uses stdlib-only methods: ast.dump for structural hashing, difflib for similarity.

Usage:
    python tools/tmp_ok/cluster_ast_fuzzy_defs.py --inventory docs/reports/sub/ast_fuzzy_inventory.json --out-json docs/reports/sub/ast_fuzzy_clusters.json
"""

import argparse
import ast
import difflib
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Similarity threshold for near-duplicates (tuned to observed distribution)
NEAR_DUPLICATE_THRESHOLD = 0.75

def extract_definition_body(file_path: str, def_name: str, def_line: int, def_kind: str) -> str | None:
    """Extract the actual body of a definition from source file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split('\n')

        if def_line > len(lines) or def_line < 1:
            return None

        # Try to extract via AST first
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == def_name and node.lineno == def_line:
                        # Extract lines from definition start to end
                        start_line = node.lineno - 1
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                        if end_line and end_line <= len(lines):
                            return '\n'.join(lines[start_line:end_line])
        except Exception:
            pass

        # Fallback: extract a reasonable chunk around the definition line
        start_idx = max(0, def_line - 1)
        end_idx = min(len(lines), start_idx + 50)  # Grab up to 50 lines
        return '\n'.join(lines[start_idx:end_idx])

    except Exception:
        return None

def normalize_tokens(text: str) -> list[str]:
    """Normalize text into tokens for similarity comparison."""
    # Remove comments and docstrings
    text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'""".*?"""', '', text, flags=re.DOTALL)
    text = re.sub(r"'''.*?'''", '', text, flags=re.DOTALL)

    # Tokenize: split on whitespace and punctuation
    tokens = re.findall(r'\w+', text.lower())
    return tokens

def calculate_structural_hash(file_path: str, def_name: str, def_line: int) -> str | None:
    """Calculate structural hash of a definition using AST dump."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == def_name and node.lineno == def_line:
                    dump = ast.dump(node, include_attributes=False)
                    return hashlib.sha256(dump.encode()).hexdigest()[:16]
    except Exception:
        pass

    return None

def calculate_text_hash(text: str) -> str:
    """Calculate hash of normalized text."""
    if not text:
        return "empty"
    normalized = '\n'.join(normalize_tokens(text))
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]

def calculate_similarity(text_a: str, text_b: str) -> float:
    """Calculate similarity between two text blocks using difflib."""
    if not text_a or not text_b:
        return 0.0

    tokens_a = normalize_tokens(text_a)
    tokens_b = normalize_tokens(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    return matcher.ratio()

def load_inventory(json_path: str) -> dict[str, Any]:
    """Load inventory JSON."""
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)

def build_clusters(inventory: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Build exact and near-duplicate clusters."""

    # Collect all definitions with their metadata
    definitions = []
    for file_data in inventory.get("files", []):
        file_path = file_data["path"]
        for candidate in file_data.get("candidates", []):
            definitions.append({
                "file": file_path,
                "name": candidate["name"],
                "line": candidate["line"],
                "kind": candidate["kind"],
                "keywords": candidate.get("keywords", [])
            })

    # Calculate hashes and extract bodies
    for defn in definitions:
        defn["struct_hash"] = calculate_structural_hash(defn["file"], defn["name"], defn["line"])
        defn["body"] = extract_definition_body(defn["file"], defn["name"], defn["line"], defn["kind"])
        defn["text_hash"] = calculate_text_hash(defn["body"]) if defn["body"] else "no_body"

    # Build exact duplicate clusters (by structural hash)
    exact_clusters_map = defaultdict(list)
    for defn in definitions:
        if defn["struct_hash"]:
            exact_clusters_map[defn["struct_hash"]].append(defn)

    exact_clusters = [
        {
            "hash": hash_val,
            "members": sorted([
                {"path": d["file"], "name": d["name"], "line": d["line"]}
                for d in members
            ], key=lambda x: (x["path"], x["line"]))
        }
        for hash_val, members in sorted(exact_clusters_map.items())
        if len(members) > 1  # Only include actual duplicates
    ]

    # Build near-duplicate pairs (by text similarity)
    near_dupe_pairs = []
    seen_pairs = set()

    for i, def_a in enumerate(definitions):
        for def_b in definitions[i+1:]:
            # Skip if already exact duplicates
            if def_a["struct_hash"] and def_a["struct_hash"] == def_b["struct_hash"]:
                continue

            # Skip if same definition
            if def_a["file"] == def_b["file"] and def_a["line"] == def_b["line"]:
                continue

            # Calculate similarity
            if def_a["body"] and def_b["body"]:
                similarity = calculate_similarity(def_a["body"], def_b["body"])

                if similarity >= NEAR_DUPLICATE_THRESHOLD:
                    pair_key = tuple(sorted([
                        (def_a["file"], def_a["line"]),
                        (def_b["file"], def_b["line"])
                    ]))

                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        near_dupe_pairs.append({
                            "a": {"path": def_a["file"], "name": def_a["name"], "line": def_a["line"]},
                            "b": {"path": def_b["file"], "name": def_b["name"], "line": def_b["line"]},
                            "score": round(similarity, 3),
                            "method": "SequenceMatcher"
                        })

    # Sort near-dupe pairs by score descending
    near_dupe_pairs.sort(key=lambda x: (-x["score"], x["a"]["path"], x["b"]["path"]))

    return exact_clusters, near_dupe_pairs

def main():
    parser = argparse.ArgumentParser(
        description="Cluster AST and fuzzy definitions into exact and near-duplicate groups"
    )
    parser.add_argument("--inventory", required=True,
                       help="Path to inventory JSON file")
    parser.add_argument("--out-json", required=True,
                       help="Output JSON file path for clusters")
    parser.add_argument("--threshold", type=float, default=NEAR_DUPLICATE_THRESHOLD,
                       help=f"Similarity threshold for near-duplicates (default: {NEAR_DUPLICATE_THRESHOLD})")

    args = parser.parse_args()

    print(f"Loading inventory from: {args.inventory}", file=sys.stderr)
    inventory = load_inventory(args.inventory)

    print(f"Building clusters (threshold: {args.threshold})...", file=sys.stderr)
    exact_clusters, near_dupe_pairs = build_clusters(inventory)

    # Generate output
    output = {
        "threshold": args.threshold,
        "exact_dupe_clusters": exact_clusters,
        "near_dupe_pairs": near_dupe_pairs,
        "summary": {
            "exact_clusters": len(exact_clusters),
            "exact_cluster_members": sum(len(c["members"]) for c in exact_clusters),
            "near_dupe_pairs": len(near_dupe_pairs)
        }
    }

    # Write JSON
    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Clusters written to: {out_path}", file=sys.stderr)
    print(f"Exact clusters: {len(exact_clusters)}, Near-dupe pairs: {len(near_dupe_pairs)}", file=sys.stderr)

if __name__ == "__main__":
    main()
