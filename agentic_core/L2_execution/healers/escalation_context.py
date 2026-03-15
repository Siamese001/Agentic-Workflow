"""
EscalationContext — Immutable escalation state with monotonicity enforcement.

retry_count is stored in a frozen dataclass and must only increase between
successive EscalationContext instances for the same trace.

EscalationContext.from_result() verifies monotonicity; a decrease in
retry_count is a HARD FAIL (signals tampering or replay violation).

Phase 3.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


class MonotonicityViolation(RuntimeError):
    """Raised when retry_count decreases between successive escalation contexts."""


@dataclass(frozen=True)
class EscalationContext:
    """Immutable snapshot of escalation state for one healing cycle step.

    Fields
    ------
    trace_id : str
        Identifier for the parent execution trace.
    retry_count : int
        Number of healing attempts so far (monotonically non-decreasing).
    healing_tier : str
        Current healing tier name (e.g. "tier_1", "tier_2").
    previous_retry_count : int
        retry_count of the immediately prior context (0 for the first).
    """

    trace_id: str
    retry_count: int
    healing_tier: str
    previous_retry_count: int = 0

    def __post_init__(self) -> None:
        if self.retry_count < 0:
            raise ValueError(f"EscalationContext: retry_count must be >= 0, got {self.retry_count}")
        if self.retry_count < self.previous_retry_count:
            raise MonotonicityViolation(
                f"EscalationContext: monotonicity violation — retry_count={self.retry_count} < previous_retry_count={self.previous_retry_count} for trace_id={self.trace_id!r}"
            )

    @classmethod
    def initial(cls, trace_id: str, healing_tier: str) -> EscalationContext:
        """Create the first EscalationContext for a trace (retry_count=0)."""
        return cls(trace_id=trace_id, retry_count=0, healing_tier=healing_tier, previous_retry_count=0)

    @classmethod
    def from_result(
        cls, previous: EscalationContext, new_healing_tier: str | None = None
    ) -> EscalationContext:
        """Create the next context after one healing attempt.

        Increments retry_count by 1 and enforces monotonicity.

        Args:
            previous: The EscalationContext from the prior step.
            new_healing_tier: Updated tier, defaults to previous tier.

        Raises:
            MonotonicityViolation: if new retry_count < previous retry_count
                (should never happen via this factory, but guards against
                 injection of a tampered *previous*).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "EscalationContext.from_result")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:EscalationContext.from_result".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        new_count = previous.retry_count + 1
        return cls(
            trace_id=previous.trace_id,
            retry_count=new_count,
            healing_tier=new_healing_tier or previous.healing_tier,
            previous_retry_count=previous.retry_count,
        )

    @property
    def is_exhausted(self) -> bool:
        """True when retry_count has reached the hard limit (5)."""
        return self.retry_count >= 5


__all__ = ["EscalationContext", "MonotonicityViolation"]
