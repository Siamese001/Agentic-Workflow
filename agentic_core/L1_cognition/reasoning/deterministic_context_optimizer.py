from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import NamedTuple, Sequence

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


@dataclass(frozen=True)
class ContextItem:
    """Represents a single item to be included in the context window."""

    content: str
    score: float
    content_hash: str


class OptimizationResult(NamedTuple):
    """The result of a context optimization operation."""

    optimized_context: Sequence[ContextItem]
    context_hash_before: str
    context_hash_after: str
    top_k_cap: int


def _compute_context_hash(items: Sequence[ContextItem]) -> str:
    """Computes a deterministic hash of the context items' identifiers."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_compute_context_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_compute_context_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "_compute_context_hash")
    sorted_hashes = sorted([item.content_hash for item in items])
    hasher = hashlib.sha256()
    for h in sorted_hashes:
        hasher.update(h.encode("utf-8"))
    return hasher.hexdigest()


def optimize_context_window(
    items: Sequence[ContextItem],
    top_k_cap: int,
    seed_pack_hash: str,
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
    sorted_items = sorted(items, key=lambda x: (-x.score, x.content_hash))
    optimized_context = sorted_items[:top_k_cap]
    context_hash_after = _compute_context_hash(optimized_context)
    return OptimizationResult(
        optimized_context=optimized_context,
        context_hash_before=context_hash_before,
        context_hash_after=context_hash_after,
        top_k_cap=top_k_cap,
    )
