"""
Canonical Serializer — single deterministic serialization authority.

All hash-producing components (HashChainAuditLog, LearningArtifactIntent,
ShiftReport, ReplayBundle) MUST use this serializer.  Direct json.dumps
usage in L2 execution paths is forbidden (enforced by AST test).

Normalization rules:
  1. Sorted keys (recursive)
  2. Tuple normalization (tuples → lists)
  3. Float precision normalization (6 decimal places, fixed format)
  4. Explicit null encoding (None → JSON null, never omitted)
  5. UTF-8 byte encoding only
  6. Compact separators (",", ":") — no whitespace variance
"""

from __future__ import annotations

import json
from typing import Any

_FLOAT_PRECISION = 6


def _normalize(obj: Any) -> Any:
    """Recursively normalize a Python object for canonical JSON.

    - dict: sorted keys, values normalized recursively
    - list/tuple: converted to list, elements normalized
    - float: rounded to fixed decimal precision
    - None: preserved (json encodes as null)
    - bool: preserved before int check (bool is subclass of int)
    - int/str: unchanged
    """
    if isinstance(obj, dict):
        return {str(k): _normalize(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}
    if isinstance(obj, (list, tuple)):
        return [_normalize(item) for item in obj]
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, float):
        return round(obj, _FLOAT_PRECISION)
    if isinstance(obj, int):
        return obj
    if obj is None:
        return None
    return str(obj)


def canonical_bytes(obj: Any) -> bytes:
    """Produce deterministic canonical bytes for hash computation.

    This is the ONLY sanctioned serialization path for governance
    hashing.  Returns UTF-8 encoded JSON with sorted keys, compact
    separators, and all normalizations applied.
    """
    normalized = _normalize(obj)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_hash(obj: Any) -> str:
    """Convenience: canonical_bytes → sha256 hex digest."""
    import hashlib

    return hashlib.sha256(canonical_bytes(obj)).hexdigest()
