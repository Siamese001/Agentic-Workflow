"""Deterministic digest helpers for L4/UWG canonical records.

The ``deterministic_digest`` field on every doctrinal record must be
reproducible across processes from stable fields only. ``canonical_json_dumps``
produces a byte-stable JSON encoding (sorted keys, no whitespace, ASCII-safe
escaping). ``compute_deterministic_digest`` SHA-256 hashes that encoding.

Forbidden inputs (per ``docs/reference/00_L4_State_and_UWG/00.5_*``):
- wall clock without explicit run-clock policy
- raw entropy
- mutable object addresses
- unsorted JSON
- non-canonical path aliases

Caller is responsible for excluding those before calling
``compute_deterministic_digest``. This module enforces canonical encoding only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_json_dumps(payload: Mapping[str, Any]) -> str:
    """Serialize ``payload`` to a canonical JSON string.

    Rules:
    - keys are sorted lexicographically at every level
    - separators are ``(",", ":")`` — no whitespace
    - ``ensure_ascii=False`` so unicode content is preserved verbatim
    - lists keep their declared order (the caller decides ordering)
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_deterministic_digest(payload: Mapping[str, Any]) -> str:
    """SHA-256 hex digest of the canonical JSON encoding of ``payload``.

    Returns a 64-character lowercase hex string. The same payload (modulo key
    order at any level) always returns the same digest.
    """
    encoded = canonical_json_dumps(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = ["canonical_json_dumps", "compute_deterministic_digest"]
