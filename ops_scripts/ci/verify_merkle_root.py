#!/usr/bin/env python3
"""W5 — Merkle Root Verifier (RTC-REQ-031, RTC-REQ-122).

Validates merkle tree depth and completeness for certification.
Per plan: Merkle root finalization + artifact chain.

Exit codes:
  0 — MERKLE_VALID (tree depth ≥ 3, all artifacts indexed)
  1 — MERKLE_EMPTY (no merkle tree found)
  2 — DEPTH_INSUFFICIENT (tree depth < 3)
  3 — INCOMPLETE_INDEX (artifacts missing from tree)

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
MERKLE_ROOT_PATH = os.environ.get("MERKLE_ROOT_PATH", "artifacts/certification/merkle_root.txt")
REQUIRED_ARTIFACTS = [
    "canonical_csv",
    "matrix_loader",
    "proof_depth_ladder",
    "acceptance_validator",
    "artifact_payload_hasher",
    "semantic_cache_probe",
    "bge_m3_operational",
    "threshold_calibration",
    "live_provider_readiness",
    "otel_collector_probe",
    "replay_verifier",
]


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


def compute_tree_depth(tree: dict[str, Any]) -> int:
    """Compute the depth of the merkle tree."""
    if not tree or "root" not in tree:
        return 0
    
    def get_depth(node: dict[str, Any]) -> int:
        if not node or "children" not in node:
            return 1
        
        children = node.get("children", [])
        if not children:
            return 1
        
        # Find max depth of children
        max_child_depth = 0
        for child in children:
            child_depth = get_depth(child)
            max_child_depth = max(max_child_depth, child_depth)
        
        return 1 + max_child_depth
    
    return get_depth(tree.get("root", {}))


def count_leaves(tree: dict[str, Any]) -> int:
    """Count leaf nodes (artifacts) in the tree."""
    if not tree or "root" not in tree:
        return 0
    
    def count_leaves_recursive(node: dict[str, Any]) -> int:
        if not node:
            return 0
        
        children = node.get("children", [])
        if not children:
            # This is a leaf
            return 1
        
        # Sum leaves in all children
        total = 0
        for child in children:
            total += count_leaves_recursive(child)
        return total
    
    return count_leaves_recursive(tree.get("root", {}))


def get_indexed_artifacts(tree: dict[str, Any]) -> set[str]:
    """Get set of artifact names indexed in the tree."""
    if not tree or "root" not in tree:
        return set()
    
    artifacts = set()
    
    def collect_artifacts(node: dict[str, Any]) -> None:
        if not node:
            return
        
        # Check if this node has an artifact name
        name = node.get("name", "")
        if name and "children" not in node:
            artifacts.add(name)
        
        # Recurse into children
        for child in node.get("children", []):
            collect_artifacts(child)
    
    collect_artifacts(tree.get("root", {}))
    return artifacts


def verify_merkle_root() -> tuple[bool, dict[str, Any]]:
    """Verify merkle tree depth and completeness.
    
    Returns: (valid, info)
    """
    tree = load_merkle_tree()
    
    if tree is None:
        return False, {"error": "MERKLE_EMPTY", "path": MERKLE_TREE_PATH}
    
    # Check depth
    depth = compute_tree_depth(tree)
    
    if depth < 3:
        return False, {
            "error": "DEPTH_INSUFFICIENT",
            "actual_depth": depth,
            "required_depth": 3,
        }
    
    # Check completeness
    indexed = get_indexed_artifacts(tree)
    missing = set(REQUIRED_ARTIFACTS) - indexed
    
    if missing:
        return False, {
            "error": "INCOMPLETE_INDEX",
            "missing_artifacts": list(missing),
            "indexed_count": len(indexed),
            "required_count": len(REQUIRED_ARTIFACTS),
        }
    
    # Check root hash present
    root_hash = tree.get("root_hash", "")
    if not root_hash:
        return False, {"error": "ROOT_HASH_MISSING"}
    
    return True, {
        "status": "MERKLE_VALID",
        "depth": depth,
        "leaf_count": count_leaves(tree),
        "indexed_artifacts": len(indexed),
        "root_hash": root_hash[:16] + "...",
    }


def emit_evidence(result: dict[str, Any]) -> None:
    """Emit evidence to artifacts directory."""
    evidence_dir = Path("artifacts/certification/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_path = evidence_dir / "merkle_root_verifier.json"
    
    evidence = {
        "verifier": "merkle_root",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tree_path": MERKLE_TREE_PATH,
        "result": result,
    }
    
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"Evidence written to: {evidence_path}")


def main() -> int:
    """Main entry point."""
    valid, info = verify_merkle_root()
    
    if not valid:
        error = info.get("error", "UNKNOWN_ERROR")
        
        if error == "MERKLE_EMPTY":
            result = {
                "status": "MERKLE_EMPTY",
                "reason": info,
            }
            emit_evidence(result)
            print(f"MERKLE EMPTY: {info}")
            return 1
        
        elif error == "DEPTH_INSUFFICIENT":
            result = {
                "status": "DEPTH_INSUFFICIENT",
                "actual_depth": info.get("actual_depth", 0),
                "required_depth": 3,
            }
            emit_evidence(result)
            print(f"DEPTH INSUFFICIENT: {info}")
            return 2
        
        elif error == "INCOMPLETE_INDEX":
            result = {
                "status": "INCOMPLETE_INDEX",
                "missing": info.get("missing_artifacts", []),
            }
            emit_evidence(result)
            print(f"INCOMPLETE INDEX: {info}")
            return 3
        
        else:
            result = {"status": "ERROR", "error": error}
            emit_evidence(result)
            print(f"ERROR: {error}")
            return 4
    
    # Success
    result = {
        "status": "MERKLE_VALID",
        "depth": info.get("depth", 0),
        "leaf_count": info.get("leaf_count", 0),
        "indexed_artifacts": info.get("indexed_artifacts", 0),
    }
    emit_evidence(result)
    
    print(f"MERKLE VALID")
    print(f"  Depth: {info.get('depth', 'N/A')}")
    print(f"  Leaves: {info.get('leaf_count', 'N/A')}")
    print(f"  Root: {info.get('root_hash', 'N/A')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
