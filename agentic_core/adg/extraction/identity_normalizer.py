"""ADG Identity Normalizer — Node identity resolution and normalization."""

from __future__ import annotations

from typing import Any


def normalize_identity(name: str) -> str:
    """Normalize a node identity name."""
    return name.strip()


def resolve_identity(adg_name: str) -> dict[str, Any]:
    """Resolve identity information from ADG name."""
    return {
        "adg_name": adg_name,
        "entity_type": "unknown",
        "layer": "UNKNOWN",
        "identity_kind": "unresolved",
        "confidence": "LOW",
    }
