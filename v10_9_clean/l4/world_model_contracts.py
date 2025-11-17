# world_model_contracts.py
"""
L4 — World Model Contracts (v10_9)

Defines canonical world fact structures and normalization helpers.
"""

from __future__ import annotations
from typing import Any, Dict, List

_ALLOWED_CATEGORIES = {"entity", "event", "relation"}
_ALLOWED_ORIGINS = {"retrieval", "user", "system"}

def normalize_world_facts(facts: List[dict]) -> List[Dict[str, Any]]:
    out = []
    for f in facts or []:
        if isinstance(f, dict):
            category = f.get("category")
            origin = f.get("origin")
            content = f.get("content")
            metadata = f.get("metadata", {})
        else:
            category, origin, content, metadata = None, None, f, {}

        out.append({
            "category": category if category in _ALLOWED_CATEGORIES else "entity",
            "origin": origin if origin in _ALLOWED_ORIGINS else "system",
            "content": "" if content is None else str(content),
            "metadata": metadata if isinstance(metadata, dict) else {},
        })
    return out
