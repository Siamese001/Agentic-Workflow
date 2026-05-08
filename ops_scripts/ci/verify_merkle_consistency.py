#!/usr/bin/env python3
"""W5 — Merkle Consistency Verifier (RTC-REQ-124).

Validates no duplicate or hollow nodes in merkle tree.
Per plan: Merkle root finalization + artifact chain.

Exit codes:
  0 — CONSISTENT (no duplicates, no hollow nodes)
  1 — DUPLICATES_FOUND (same artifact appears multiple times)
  2 — HOLLOW_NODES_FOUND (empty intermediate nodes)
  3 — HASH_MISMATCH (computed hash != stored hash)
  4 — TREE_MISSING (no merkle tree to validate)

W5 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
MERKLE_TREE_PATH = os.environ.get("MERKLE_TREE_PATH", "artifacts/certification/merkle_tree.json")


def load_merkle_tree() -> dict[str, Any] | None:
    """Load merkle tree if it exists."""
    tree_path = Path(MERKLE_TREE_PATH)
    
    if not tree_path.exists():
        return None
    
    try:
        with open(tree_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def find_duplicates(tree: dict[str, Any]) -> dict[str, int]:
    """Find duplicate artifact names in the tree."""
    name_counts: dict[str, int] = {}
    
    def count_names(node: dict[str, Any]) -> None:
        if not node:
            return
        
        name = node.get("name", "")
        if name:
            name_counts[name] = name_counts.get(name, 0) + 1
        
        for child in node.get("children", []):
            count_names(child)
    
    if tree and "root" in tree:
        count_names(tree.get("root", {}))
    
    # Return only names with count > 1
    return {name: count for name, count in name_counts.items() if count > 1}


def find_hollow_nodes(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Find hollow (empty) intermediate nodes in the tree."""
    hollow = []
    
    def check_hollow(node: dict[str, Any], path: str = "root") -> None:
        if not node:
            return
        
        children = node.get("children", [])
        name = node.get("name", "")
        
        # A hollow node has children but no name/hash
        if children and not name and "hash" not in node:
            hollow.append({
                "path": path,
                "child_count": len(children),
            })
        
        # Recurse
        for i, child in enumerate(children):
            check_hollow(child, f"{path}/{i}")
    
    if tree and "root" in tree:
        check_hollow(tree.get("root", {}))
    
    return hollow


def compute_node_hash(node: dict[str, Any]) -> str:
    """Compute hash for a node from its children."""
    if not node:
        return ""
    
    # If leaf node, hash the name + data
    children = node.get("children", [])
    if not children:
        name = node.get("name", "")
        data = node.get("data", "")
        content = f"{name}:{data}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    # If intermediate node, hash concatenation of child hashes
    child_hashes = []
    for child in children:
        child_hash = compute_node_hash(child)
        if child_hash:
            child_hashes.append(child_hash)
    
    if not child_hashes:
        return ""
    
    combined = "".join(sorted(child_hashes))
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def verify_hash_consistency(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Verify stored hashes match computed hashes."""
    mismatches = []
    
    def check_node(node: dict[str, Any], path: str = "root") -> None:
        if not node:
            return
        
        stored_hash = node.get("hash", "")
        if stored_hash:
            computed = compute_node_hash(node)
            if computed and computed != stored_hash:
                mismatches.append({
                    "path": path,
                    "stored": stored_hash[:16] + "...",
                    "computed": computed[:16] + "...",
                })
        
        # Recurse
        for i, child in enumerate(node.get("children", [])):
            check_node(child, f"{path}/{i}")
    
    if tree and "root" in tree:
        check_node(tree.get("root", {}))
    
    return mismatches


def verify_consistency() -> tuple[bool, dict[str, Any]]:
    """Verify merkle tree consistency.
    
    Returns: (consistent, info)
    """
    tree = load_merkle_tree()
    
    if tree is None:
        return False, {"error": "TREE_MISSING", "path": MERKLE_TREE_PATH}
    
    # Check for duplicates
    duplicates = find_duplicates(tree)
    if duplicates:
        return False, {
            "error": "DUPLICATES_FOUND",
            "duplicates": duplicates,
        }
    
    # Check for hollow nodes
    hollow = find_hollow_nodes(tree)
    if hollow:
        return False, {
            "error": "HOLLOW_NODES_FOUND",
            "hollow_nodes": hollow,
        }
    
    # Check hash consistency
    mismatches = verify_hash_consistency(tree)
    if mismatches:
        return False, {
            "error": "HASH_MISMATCH",
            "mismatches": mismatches,
        }
    
    return True, {
        "status": "CONSISTENT",
        "node_count": count_nodes(tree),
        "leaf_count": count_leaves(tree),
    }


def count_nodes(tree: dict[str, Any]) -> int:
    """Count total nodes in tree."""
    def count_recursive(node: dict[str, Any]) -> int:
        if not node:
            return 0
        
        total = 1  # Count this node
        for child in node.get("children", []):
            total += count_recursive(child)
        return total
    
    if tree and "root" in tree:
        return count_recursive(tree.get("root", {}))
    return 0


def count_leaves(tree: dict[str, Any]) -> int:
    """Count leaf nodes in tree."""
    def count_recursive(node: dict[str, Any]) -> int:
        if not node:
            return 0
        
        children = node.get("children", [])
        if not children:
            return 1
        
        total = 0
        for child in children:
            total += count_recursive(child)
        return total
    
    if tree and "root" in tree:
        return count_recursive(tree.get("root", {}))
    return 0


def emit_evidence(result: dict[str, Any]) -> None:
    """Emit evidence to artifacts directory."""
    evidence_dir = Path("artifacts/certification/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_path = evidence_dir / "merkle_consistency_verifier.json"
    
    evidence = {
        "verifier": "merkle_consistency",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tree_path": MERKLE_TREE_PATH,
        "result": result,
    }
    
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"Evidence written to: {evidence_path}")


def main() -> int:
    """Main entry point."""
    consistent, info = verify_consistency()
    
    if not consistent:
        error = info.get("error", "UNKNOWN_ERROR")
        
        if error == "TREE_MISSING":
            result = {"status": "TREE_MISSING", "reason": info}
            emit_evidence(result)
            print(f"TREE MISSING: {info}")
            return 4
        
        elif error == "DUPLICATES_FOUND":
            result = {
                "status": "DUPLICATES_FOUND",
                "duplicates": info.get("duplicates", {}),
            }
            emit_evidence(result)
            print(f"DUPLICATES FOUND: {info}")
            return 1
        
        elif error == "HOLLOW_NODES_FOUND":
            result = {
                "status": "HOLLOW_NODES_FOUND",
                "hollow": info.get("hollow_nodes", []),
            }
            emit_evidence(result)
            print(f"HOLLOW NODES: {info}")
            return 2
        
        elif error == "HASH_MISMATCH":
            result = {
                "status": "HASH_MISMATCH",
                "mismatches": info.get("mismatches", []),
            }
            emit_evidence(result)
            print(f"HASH MISMATCH: {info}")
            return 3
        
        else:
            result = {"status": "ERROR", "error": error}
            emit_evidence(result)
            print(f"ERROR: {error}")
            return 5
    
    # Success
    result = {
        "status": "CONSISTENT",
        "node_count": info.get("node_count", 0),
        "leaf_count": info.get("leaf_count", 0),
    }
    emit_evidence(result)
    
    print(f"MERKLE CONSISTENT")
    print(f"  Nodes: {info.get('node_count', 'N/A')}")
    print(f"  Leaves: {info.get('leaf_count', 'N/A')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
