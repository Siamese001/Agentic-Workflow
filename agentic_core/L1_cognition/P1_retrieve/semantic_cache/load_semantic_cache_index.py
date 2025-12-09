# Ownership: agentic_core / L1_cognition
# Layer: L1_cognition
# Agent: agentic_core
# -*- coding: utf-8 -*-
"""Load semantic cache index from storage."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_semantic_cache_index(cache_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load the semantic cache index from disk.

    Args:
        cache_path: Path to the cache index file

    Returns:
        Cache index dictionary or None if not found
    """
    if not cache_path.exists():
        return None

    try:
        content = cache_path.read_text(encoding="utf-8")
        return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return None


def load_cache_metadata(cache_dir: Path) -> Dict[str, Any]:
    """
    Load metadata about the semantic cache.

    Args:
        cache_dir: Directory containing cache files

    Returns:
        Metadata dictionary with cache statistics
    """
    metadata = {
        "total_entries": 0,
        "cache_version": "1.0",
        "last_updated": None,
    }

    index_path = cache_dir / "index.json"
    index = load_semantic_cache_index(index_path)

    if index:
        metadata["total_entries"] = len(index.get("entries", []))
        metadata["last_updated"] = index.get("updated_at")

    return metadata
