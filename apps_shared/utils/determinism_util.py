"""
Shared determinism utility for apps_lic and apps_rg.

Provides canonical hashing and recursive nondeterminism stripping
bound to the canonical_bytes() function from the L0 spine.

All hashing delegates to:
    agentic_core.L0_routing.engines.assembly_stage.canonical_bytes

No local canonicalization is performed here.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from agentic_core.interfaces.determinism import canonical_bytes

DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {"duration_ms", "timestamp", "trace_id", "cycle_counter", "telemetry", "created_at", "updated_at"}
)


def strip_nondeterministic(obj: Any) -> Any:
    """Recursively strip nondeterministic fields from obj.

    Rules:
    - dict: drop keys in DETERMINISM_EXCLUDED_FIELDS at any depth; recurse values.
    - list/tuple: recurse each element, preserve order and type.
    - anything else: return as-is.

    This function is recursion-safe and deterministic.
    It never introduces wall-clock time or randomness.
    """
    if isinstance(obj, dict):
        return {k: strip_nondeterministic(v) for k, v in obj.items() if k not in DETERMINISM_EXCLUDED_FIELDS}
    if isinstance(obj, tuple):
        return tuple(strip_nondeterministic(item) for item in obj)
    if isinstance(obj, list):
        return [strip_nondeterministic(item) for item in obj]
    return obj


def canonical_hash(obj: Any) -> str:
    """Return sha256 hexdigest of canonical_bytes(strip_nondeterministic(obj)).

    obj must be a dict (or list/tuple of dicts) serialisable by canonical_bytes.
    Excluded fields are stripped recursively before hashing.
    """
    stripped = strip_nondeterministic(obj)
    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()


def file_hash(path: str | Path) -> str:
    """Return sha256 hexdigest of the raw bytes of the file at path."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
