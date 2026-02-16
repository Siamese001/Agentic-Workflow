#!/usr/bin/env python3
"""
Deterministic clustering of AST + fuzzy library definitions.

Clusters candidates by:
1. Exact match: ast.dump(node) SHA256 for parsed defs, normalized text SHA256 for fallback
2. Fuzzy match: difflib.SequenceMatcher ratio on tokenized bodies

Output: deterministic JSON with sorted ordering.
"""

import ast
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


def load_inventory(inventory_path: Path) -> dict[str, Any]:
    """Load the inventory JSON."""
    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


def tokenize_simple(text: str) -> list[str]:
    """Simple tokenization: split on whitespace and punctuation."""
    # Remove comments and strings for better matching
    text = re.sub(r"#.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r'""".*?"""', "", text, flags=re.DOTALL)
    text = re.sub(r"'''.*?'''", "", text, flags=re.DOTALL)
    text = re.sub(r'"[^"]*"', "", text)
    text = re.sub(r"'[^']*'", "", text)

    # Tokenize
    tokens = re.findall(r"\w+", text.lower())
    return tokens


def compute_exact_hash(file_path: str, candidate: dict[str, Any], repo_root: Path) -> str | None:
    """Compute exact hash for a candidate definition."""
    try:
        full_path = repo_root / file_path
        source = full_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)

        # Find the matching node
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == candidate["name"] and node.lineno == candidate["line"]:
                    # Dump the node (without attributes for stability)
                    dump_str = ast.dump(node, include_attributes=False)
                    return hashlib.sha256(dump_str.encode()).hexdigest()

        # Fallback: use normalized text slice
        lines = source.split("\n")
        start_line = candidate["line"] - 1
        if start_line < len(lines):
            text_slice = lines[start_line]
            normalized = re.sub(r"\s+", " ", text_slice).strip()
            return hashlib.sha256(normalized.encode()).hexdigest()

    except (SyntaxError, UnicodeDecodeError, OSError):
        return None

    return None


def build_exact_clusters(inventory: dict[str, Any], repo_root: Path) -> dict[str, list[dict[str, Any]]]:
    """Build exact duplicate clusters."""
    clusters = {}

    for file_entry in inventory["files"]:
        for candidate in file_entry["candidates"]:
            exact_hash = compute_exact_hash(file_entry["path"], candidate, repo_root)
            if exact_hash:
                if exact_hash not in clusters:
                    clusters[exact_hash] = []
                clusters[exact_hash].append(
                    {
                        "path": file_entry["path"],
                        "name": candidate["name"],
                        "line": candidate["line"],
                        "kind": candidate["kind"],
                    }
                )

    return clusters


def compute_similarity(text1: str, text2: str) -> float:
    """Compute similarity ratio using difflib."""
    tokens1 = tokenize_simple(text1)
    tokens2 = tokenize_simple(text2)

    if not tokens1 or not tokens2:
        return 0.0

    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    return matcher.ratio()


def extract_body_text(file_path: str, candidate: dict[str, Any], repo_root: Path) -> str | None:
    """Extract the body text of a candidate definition."""
    try:
        full_path = repo_root / file_path
        source = full_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == candidate["name"] and node.lineno == candidate["line"]:
                    return ast.unparse(node) if hasattr(ast, "unparse") else None

        # Fallback: extract lines
        lines = source.split("\n")
        start_line = candidate["line"] - 1
        if start_line < len(lines):
            return lines[start_line]

    except (SyntaxError, UnicodeDecodeError, OSError):
        return None

    return None


FUZZY_SIMILARITY_THRESHOLD = float(os.environ.get("AST_FUZZY_THRESHOLD", "0.6"))


def build_fuzzy_pairs(
    inventory: dict[str, Any], repo_root: Path, threshold: float = FUZZY_SIMILARITY_THRESHOLD
) -> list[dict[str, Any]]:
    """Build near-duplicate pairs using fuzzy matching."""
    pairs = []
    candidates_list = []

    # Flatten candidates with file context
    for file_entry in inventory["files"]:
        for candidate in file_entry["candidates"]:
            candidates_list.append(
                {
                    "file": file_entry["path"],
                    "candidate": candidate,
                    "body": extract_body_text(file_entry["path"], candidate, repo_root),
                }
            )

    # Compare all pairs
    seen = set()
    for i, item1 in enumerate(candidates_list):
        for item2 in candidates_list[i + 1 :]:
            if not item1["body"] or not item2["body"]:
                continue

            score = compute_similarity(item1["body"], item2["body"])
            if score >= threshold:
                pair_key = tuple(
                    sorted(
                        [
                            (item1["file"], item1["candidate"]["name"], item1["candidate"]["line"]),
                            (item2["file"], item2["candidate"]["name"], item2["candidate"]["line"]),
                        ]
                    )
                )

                if pair_key not in seen:
                    seen.add(pair_key)
                    pairs.append(
                        {
                            "a": {
                                "path": item1["file"],
                                "name": item1["candidate"]["name"],
                                "line": item1["candidate"]["line"],
                            },
                            "b": {
                                "path": item2["file"],
                                "name": item2["candidate"]["name"],
                                "line": item2["candidate"]["line"],
                            },
                            "score": round(score, 4),
                            "method": "SequenceMatcher",
                        }
                    )

    return sorted(pairs, key=lambda x: (-x["score"], x["a"]["path"], x["b"]["path"]))


def main():
    """Main entry point."""
    repo_root = Path.cwd()
    inventory_path = repo_root / "docs" / "reports" / "sub" / "ast_fuzzy_inventory.json"

    if not inventory_path.exists():
        print(f"Error: {inventory_path} not found")
        return 1

    print("Loading inventory...")
    inventory = load_inventory(inventory_path)

    print("Building exact clusters...")
    exact_clusters = build_exact_clusters(inventory, repo_root)

    # Filter to only clusters with 2+ members
    exact_clusters_filtered = {k: v for k, v in exact_clusters.items() if len(v) >= 2}

    print(f"Found {len(exact_clusters_filtered)} exact duplicate clusters")

    print(f"Building fuzzy pairs (threshold={FUZZY_SIMILARITY_THRESHOLD})...")
    fuzzy_pairs = build_fuzzy_pairs(inventory, repo_root, threshold=FUZZY_SIMILARITY_THRESHOLD)

    print(f"Found {len(fuzzy_pairs)} near-duplicate pairs (score >= 0.6)")

    # Build output
    output = {
        "exact_dupe_clusters": [
            {"hash": hash_val, "members": sorted(members, key=lambda x: (x["path"], x["name"]))}
            for hash_val, members in sorted(exact_clusters_filtered.items())
        ],
        "near_dupe_pairs": fuzzy_pairs,
    }

    # Write output
    output_path = repo_root / "docs" / "reports" / "sub" / "ast_fuzzy_clusters.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Output written to: {output_path}")
    print(f"SHA256: {_file_sha256(output_path)}")

    return 0


def _file_sha256(path: Path) -> str:
    """Compute SHA256 of file."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


if __name__ == "__main__":
    exit(main())
