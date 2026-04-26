"""Deterministic replay-digest helpers for L1 v6 stages.

Doctrine reference: every 02.X file's PHASE 5 REPLAY / HASH REQUIREMENTS.

Digest inputs MUST exclude wall-clock time, nondeterministic memory IDs,
transient span IDs, provider latency, and local filesystem temp names.
Digest inputs MUST include the canonical serialized output fields, the
normalized request hash, the scoped visible context hash, and the
policy / instruction hashes observed.

This module provides exactly two helpers: :func:`stable_digest` (sha256
over a sorted-key JSON canonical encoding of any json-safe payload) and
:func:`canonical_payload` (recursively normalises tuples / dataclass
``to_dict()`` outputs into a json-safe shape).

No dependency on time, uuid, randomness, or environment.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

__all__ = [
    "canonical_payload",
    "stable_digest",
    "DETERMINISTIC_DIGEST_ALGORITHM",
]

DETERMINISTIC_DIGEST_ALGORITHM = "sha256-canonical-json-v1"


def canonical_payload(value: Any) -> Any:
    """Normalise ``value`` into a json-safe, deterministic shape.

    Tuples become lists; dataclasses with a ``to_dict`` method are reduced
    to that dict; sets become sorted lists; everything else passes through
    if json-serialisable. ``None`` and primitives pass through unchanged.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return canonical_payload(value.to_dict())
    if isinstance(value, dict):
        return {str(k): canonical_payload(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical_payload(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(canonical_payload(v) for v in value)
    # Enum (closed) — serialise by .value when available.
    if hasattr(value, "value") and not callable(value.value):
        return canonical_payload(value.value)
    # Fallback: string repr (deterministic for the same object).
    return str(value)


def stable_digest(payload: Any, *, prefix: str = "") -> str:
    """Compute the canonical replay digest for ``payload``.

    Args:
        payload: any json-safe nested structure.
        prefix: optional short string baked into the hash domain so two
            stages with identical canonical payloads still produce
            different digests. The default empty string preserves the
            hash domain for callers that do not care.

    Returns:
        ``"sha256:<hexdigest>"``.
    """
    canonical = canonical_payload(payload)
    serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    h = hashlib.sha256()
    if prefix:
        h.update(prefix.encode("utf-8"))
        h.update(b"\x00")
    h.update(serialized)
    return f"sha256:{h.hexdigest()}"
