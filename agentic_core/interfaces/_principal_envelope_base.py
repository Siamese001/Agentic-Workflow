"""Shared building blocks for principal-aware write and egress envelopes.

`principal_aware_write.py` (W2) and `principal_aware_egress.py` (W3) both
follow the same pattern:

  1. Compute a SHA-256 over the canonical PrincipalChain dict.
  2. Compute an extended replay key that binds an operation-specific
     payload to that principal digest.
  3. Wrap the result in an immutable, frozen dataclass envelope with
     `__post_init__` validation that every required string is non-empty.

This module hosts the pieces those two adapters share so the per-surface
files can stay focused on their surface-specific shape (write vs egress)
without re-implementing the envelope plumbing.

Reference: identity_propagation.md §3.4–§3.6 (G-04 W2/W3).
"""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from agentic_core.interfaces.principal_chain_types import PrincipalChain


def compute_principal_chain_digest(chain: PrincipalChain) -> str:
    """SHA-256 over the deterministic dict form of a `PrincipalChain`.

    Centralized here so both the write- and egress-side adapters use the
    same canonicalization (sort_keys + compact separators) — divergence
    here would silently break replay-envelope reconstruction.
    """
    canonical = json.dumps(chain.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compose_replay_key(payload: dict[str, object]) -> str:
    """Hash an arbitrary, JSON-serializable, key-stable payload.

    Both write (W2) and egress (W3) replay keys are SHA-256 hashes of a
    canonical JSON serialization of a small dict. This helper enforces
    `sort_keys=True` + compact separators so the hash is reproducible
    regardless of dict insertion order.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def require_nonempty(values: Iterable[tuple[str, str | None]]) -> None:
    """Raise `ValueError` on the first ``(name, value)`` pair where value is falsy.

    Replaces the repeated ``if not self.X: raise ValueError("...: X required")``
    chain in each envelope's ``__post_init__``. Accepts ``str | None`` so
    ``__post_init__`` callers can pass an Optional-typed attribute directly
    without a cast — both empty-string and None correctly raise.

    Caller passes pairs as ``[("plan_hash", self.plan_hash), ...]`` and the
    helper raises with the same message shape the prior inline checks used.
    """
    for name, value in values:
        if not value:
            raise ValueError(f"{name} required")


__all__ = [
    "compose_replay_key",
    "compute_principal_chain_digest",
    "require_nonempty",
]
