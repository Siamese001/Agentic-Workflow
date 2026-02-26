from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import NamedTuple, Sequence


# Placeholder for a more complex document/context object.
@dataclass(frozen=True)
class ContextItem:
    """Represents a single item to be included in the context window."""

    content: str
    score: float  # e.g., relevance score from a retrieval system
    content_hash: str  # Pre-computed SHA-256 hash of the content


class OptimizationResult(NamedTuple):
    """The result of a context optimization operation."""

    optimized_context: Sequence[ContextItem]
    context_hash_before: str  # Hash of the context identifiers before optimization
    context_hash_after: str  # Hash of the context identifiers after optimization
    top_k_cap: int


def _compute_context_hash(items: Sequence[ContextItem]) -> str:
    """Computes a deterministic hash of the context items' identifiers."""
    # Sorting by content_hash ensures a stable order.
    sorted_hashes = sorted([item.content_hash for item in items])
    hasher = hashlib.sha256()
    for h in sorted_hashes:
        hasher.update(h.encode("utf-8"))
    return hasher.hexdigest()


def optimize_context_window(
    items: Sequence[ContextItem],
    top_k_cap: int,
    seed_pack_hash: str,  # For determinism digest inclusion
) -> OptimizationResult:
    """
    Optimizes the context window with deterministic ordering and capping.

    This function enforces Guarantee #3 by ensuring that the context slicing
    is stable, replayable, and does not suffer from non-determinism due to
    unstable sorting of items with equal scores.

    Args:
        items: The full list of candidate items for the context window.
        top_k_cap: The maximum number of items to include in the final context.
        seed_pack_hash: The hash of the embedding pack, used for replay binding.

    Returns:
        An OptimizationResult containing the sliced context and determinism hashes.
    """
    if not items:
        empty_hash = hashlib.sha256(b"").hexdigest()
        return OptimizationResult(
            optimized_context=[],
            context_hash_before=empty_hash,
            context_hash_after=empty_hash,
            top_k_cap=top_k_cap,
        )

    context_hash_before = _compute_context_hash(items)

    # 1. Deterministic Ordering: Sort by score (desc), then content_hash (asc).
    #    This provides a stable tie-breaker if scores are equal.
    sorted_items = sorted(items, key=lambda x: (-x.score, x.content_hash))

    # 2. Top-K Capping: Slice the list to the maximum allowed size.
    optimized_context = sorted_items[:top_k_cap]

    # 3. Emit Determinism Artifacts: Compute the hash of the final context.
    context_hash_after = _compute_context_hash(optimized_context)

    # The digest contribution would also include the seed_pack_hash.
    # digest_material = {
    #     "context_hash_before": context_hash_before,
    #     "context_hash_after": context_hash_after,
    #     "top_k_cap": top_k_cap,
    #     "seed_pack_hash": seed_pack_hash,
    # }

    return OptimizationResult(
        optimized_context=optimized_context,
        context_hash_before=context_hash_before,
        context_hash_after=context_hash_after,
        top_k_cap=top_k_cap,
    )
