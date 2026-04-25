"""PA.7 — Idempotency Nonce + Prompt-Cache Prefix Discipline.

Two related concerns combined in one module to keep the surface area small:

1. **Idempotency nonce** (G10) — generates a stable, deterministic nonce given
   a `(trace_id, attempt_number)` pair. Used by gateways that need exact-once
   semantics for retries without breaking replay-key determinism.

2. **Prompt-cache prefix discipline** (G14) — exposes a `cache_prefix_hash`
   helper that hashes the stable S0+D0+I0 block. Providers like Anthropic and
   OpenAI key prompt caching on a stable prefix; this gives callers a
   deterministic way to detect prefix drift across calls.

Doctrinal anchor: docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md PA.7
Plan: prompt-assembly-best-practices-gap-b4e1c2 W6 (G10, G14)

Determinism contract:
  - `compute_nonce(trace_id, attempt)` returns the same 32-char hex for the
    same inputs across any process or machine.
  - `cache_prefix_hash(slots)` returns the same 16-char hex when S0+D0+I0
    are byte-identical, even if other slots differ.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


# Stable namespace prefix — bumped only on incompatible scheme changes.
_NONCE_NAMESPACE: str = "pa7-nonce-v1"
_CACHE_PREFIX_NAMESPACE: str = "pa7-cache-v1"

# Slots that form the stable cache prefix per PA.5 "stable prefix discipline".
_CACHE_PREFIX_SLOTS: tuple[str, ...] = ("S0", "D0", "I0")


@dataclass(frozen=True)
class IdempotencyEnvelope:
    """Container for nonce + prefix hash, attachable to GovernedPayload."""

    nonce: str
    cache_prefix_hash: str
    attempt: int
    trace_id: str
    scheme_version: str = "v1"


def compute_nonce(trace_id: str, attempt: int = 0) -> str:
    """Compute deterministic idempotency nonce for `(trace_id, attempt)`.

    Returns the same 32-char hex digest for identical inputs across any
    process. Suitable for OpenAI's `Idempotency-Key` header and Anthropic's
    `request-id` semantics.

    Args:
        trace_id: Stable per-request identifier from the BOM.
        attempt: 0-indexed retry attempt number. Different attempts yield
                 distinct nonces so retries don't collide with the original.

    Returns:
        Lowercase 32-char hex string (128-bit truncated SHA-256).
    """
    if not trace_id:
        raise ValueError("trace_id is required for nonce computation")
    if attempt < 0:
        raise ValueError(f"attempt must be >= 0, got {attempt}")

    payload = f"{_NONCE_NAMESPACE}|{trace_id}|{attempt}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    # Truncate to 128 bits = 32 hex chars (collision risk negligible per request)
    return digest[:32]


def cache_prefix_hash(slots: dict[str, str]) -> str:
    """Compute stable hash of the prompt-cache prefix (S0+D0+I0).

    Anthropic prompt caching and OpenAI cached prefix detection both key on
    the stable opening of the system message. This helper lets callers
    confirm the prefix has not drifted between calls.

    Args:
        slots: Slot dict as produced by AirlockAssembler.

    Returns:
        Lowercase 16-char hex string. Empty slots are treated as empty
        string (not absent) so a missing S0 hashes deterministically.
    """
    canonical_lines = []
    for slot_name in _CACHE_PREFIX_SLOTS:
        content = slots.get(slot_name, "") or ""
        # Normalize line endings for cross-platform stability
        content = content.replace("\r\n", "\n").replace("\r", "\n").strip()
        canonical_lines.append(f"{slot_name}={content}")
    payload = (_CACHE_PREFIX_NAMESPACE + "|" + "\n".join(canonical_lines)).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return digest[:16]


def make_envelope(trace_id: str, slots: dict[str, str], attempt: int = 0) -> IdempotencyEnvelope:
    """Build a complete idempotency envelope for a single request attempt."""
    return IdempotencyEnvelope(
        nonce=compute_nonce(trace_id, attempt),
        cache_prefix_hash=cache_prefix_hash(slots),
        attempt=attempt,
        trace_id=trace_id,
    )


def detect_prefix_drift(previous_hash: str, current_slots: dict[str, str]) -> bool:
    """Return True if the cache prefix has drifted since `previous_hash`.

    Use case: gateway holds a replay log; on retry it checks whether the
    cached prefix is still valid before re-using a provider-side cache key.
    """
    return cache_prefix_hash(current_slots) != previous_hash
