"""Deterministic digest helpers for the E2E proof harness.

All digests use blake2b for stability + speed and JSON canonicalization
(sort_keys, no whitespace, ensure_ascii) so the same logical artifact always
produces the same digest regardless of dict ordering or platform.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Serialize ``obj`` to canonical JSON used for digesting."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=_default)


def digest(obj: Any, *, prefix: str = "blake2b") -> str:
    """Return a stable hex digest of ``obj``.

    Parameters
    ----------
    obj:
        Any JSON-serializable Python object.
    prefix:
        Algorithm prefix included in the returned string ("<prefix>:<hex>").
    """
    payload = canonical_json(obj).encode("utf-8")
    h = hashlib.blake2b(payload, digest_size=16)
    return f"{prefix}:{h.hexdigest()}"


def short_id(obj: Any, *, length: int = 8) -> str:
    """Return the first ``length`` hex chars of the digest, no prefix."""
    return digest(obj).split(":", 1)[1][:length]


def _default(value: Any) -> Any:
    """Fallback serializer used by ``canonical_json``.

    Dataclasses, sets, and tuples are normalized to JSON-friendly forms.
    Anything else falls through as ``repr`` so digests stay deterministic.
    """
    from dataclasses import asdict, is_dataclass

    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    if isinstance(value, tuple):
        return list(value)
    return repr(value)


__all__ = ["canonical_json", "digest", "short_id"]
