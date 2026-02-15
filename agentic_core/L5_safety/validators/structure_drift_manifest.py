"""
Structure Drift Manifest - Deterministic Layer Topology Snapshot

Generates a deterministic manifest of L* layer structure and utils/ inventory.
Used for drift detection to prevent structural blueprint staleness.

DETERMINISM GUARANTEES:
- Sorted layer names, sorted file paths
- POSIX-style paths (forward slashes)
- Stable JSON formatting (sorted keys, no whitespace)
- SHA-256 hash over canonical bytes
- No timestamps, UUIDs, host paths, or nondeterministic fields

USAGE:
    from agentic_core.L5_safety.validators.structure_drift_manifest import (
        generate_manifest,
        canonical_manifest_bytes,
        manifest_hash,
    )

    manifest = generate_manifest(Path("agentic_core"))
    hash_value = manifest_hash(manifest)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def generate_manifest(root: Path) -> dict[str, Any]:
    """
    Generate deterministic manifest of L* layer topology.

    Args:
        root: Path to agentic_core directory

    Returns:
        Dict with structure:
        {
            "L0_routing": {
                "has_utils": true,
                "utils_files": ["L0_routing/utils/file1.py", ...]
            },
            ...
        }

    Determinism:
        - Layers sorted alphabetically
        - File paths sorted alphabetically
        - Paths normalized to POSIX (forward slashes)
        - Relative to root parameter
    """
    manifest: dict[str, Any] = {}

    # Enumerate all L* directories directly under root
    layers = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("L")])

    for layer in layers:
        utils_dir = layer / "utils"
        has_utils = utils_dir.exists()

        utils_files: list[str] = []
        if has_utils:
            # Recursively find all *.py files under utils/
            py_files = sorted(utils_dir.rglob("*.py"))
            # Convert to POSIX-style relative paths from root
            utils_files = [str(p.relative_to(root).as_posix()) for p in py_files]

        manifest[layer.name] = {
            "has_utils": has_utils,
            "utils_files": utils_files,
        }

    return manifest


def canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    """
    Convert manifest to canonical byte representation.

    Args:
        manifest: Manifest dict from generate_manifest()

    Returns:
        UTF-8 encoded JSON bytes with deterministic formatting

    Format:
        - Sorted keys
        - Compact separators (no spaces)
        - ASCII-only encoding
        - Newline-terminated
    """
    json_str = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return (json_str + "\n").encode("utf-8")


def manifest_hash(manifest: dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of manifest.

    Args:
        manifest: Manifest dict from generate_manifest()

    Returns:
        Hex-encoded SHA-256 hash string (64 characters)

    Determinism:
        - Hash computed over canonical_manifest_bytes()
        - Same manifest always produces same hash
    """
    canonical_bytes = canonical_manifest_bytes(manifest)
    return hashlib.sha256(canonical_bytes).hexdigest()


__all__ = [
    "generate_manifest",
    "canonical_manifest_bytes",
    "manifest_hash",
]
