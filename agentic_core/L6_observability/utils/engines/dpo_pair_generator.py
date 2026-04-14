from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    record_execution_trace,
)

record_execution_trace("dpo_pair_generator", "dpo_pair_generator_trace")


class BoundingViolation(Exception):
    """Raised when a DPO feedback value is outside the allowed bounds."""


@dataclass(frozen=True)
class DPOPair:
    """Represents a chosen/rejected pair for Direct Preference Optimization."""

    control_hash: str
    candidate_hash: str
    control_payload: Any
    candidate_payload: Any
    raw_score: float


class BoundedDPOPair(NamedTuple):
    """A DPO pair with its score bounded and clamped."""

    pair: DPOPair
    bounded_score: float


@dataclass(frozen=True)
class DPOBoundingPolicy:
    """Defines the sovereign policy for bounding DPO feedback."""

    min_clamp: float = 0.1
    max_clamp: float = 2.0
    max_delta: float = 0.1


def create_bounded_dpo_pairs(pairs: list[DPOPair], policy: DPOBoundingPolicy) -> list[BoundedDPOPair]:
    """
    Processes a list of DPO pairs, applying sovereign bounding and sorting.

    This function enforces Guarantee #23 by:
    1. Sorting pairs deterministically to prevent reordering on replay.
    2. Clamping raw scores to a fixed range [0.1, 2.0].
    3. Limiting the maximum change (delta) from a neutral score (1.0).

    Args:
        pairs: The list of raw DPO pairs to process.
        policy: The bounding policy to apply.

    Returns:
        A list of bounded DPO pairs, ready for meta-learning.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "create_bounded_dpo_pairs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "create_bounded_dpo_pairs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "create_bounded_dpo_pairs")
    sorted_pairs = sorted(pairs, key=lambda p: (p.control_hash, p.candidate_hash))
    bounded_pairs: list[BoundedDPOPair] = []
    for pair in sorted_pairs:
        clamped_score = max(policy.min_clamp, min(pair.raw_score, policy.max_clamp))
        delta = clamped_score - 1.0
        if abs(delta) > policy.max_delta:
            bounded_score = 1.0 + (policy.max_delta if delta > 0 else -policy.max_delta)
        else:
            bounded_score = clamped_score
        bounded_pairs.append(BoundedDPOPair(pair=pair, bounded_score=bounded_score))
    return bounded_pairs
