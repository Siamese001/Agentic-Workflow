"""
L2 Re-Entry Loop - Bounded Deterministic Retry Mechanism

Implements bounded retry logic with deterministic behavior.
No infinite loops, no sleep/time usage, pure deterministic behavior.
"""

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


class ReEntryLoop:
    """
    Bounded deterministic re-entry loop for execution cycles.

    Provides retry logic with maximum attempt limits.
    No infinite loops, no sleep/time usage.
    """

    def __init__(self, max_attempts: int, cid_registry: CIDRegistry = None):
        """
        Initialize ReEntryLoop with maximum attempts.

        Args:
            max_attempts: Maximum number of attempts allowed
            cid_registry: Optional CIDRegistry instance
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReEntryLoop.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReEntryLoop.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReEntryLoop.__init__")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.max_attempts = max_attempts
        self._cid_registry = cid_registry or CIDRegistry()

    def should_retry(self, cycle: ExecutionCycle) -> bool:
        """
        Determine if execution cycle should be retried.

        Args:
            cycle: Current execution cycle

        Returns:
            True if cycle.attempt < max_attempts
        """
        return cycle.attempt < self.max_attempts

    def advance(self, cycle: ExecutionCycle) -> ExecutionCycle:
        """
        Advance to next attempt cycle.

        Calls CIDRegistry.next_attempt.

        Args:
            cycle: Current execution cycle

        Returns:
            Next execution cycle with incremented attempt
        """
        return self._cid_registry.next_attempt(cycle)

    def new_cycle(self, cid: str) -> ExecutionCycle:
        """
        Create new execution cycle for given CID.

        Args:
            cid: Correlation ID for the cycle

        Returns:
            New ExecutionCycle with attempt=1
        """
        return self._cid_registry.new_cycle(cid)

    def get_cycle(self, cid: str):
        """
        Get current cycle for given CID.

        Args:
            cid: Correlation ID to lookup

        Returns:
            Current ExecutionCycle or None if not found
        """
        return self._cid_registry.get_cycle(cid)

    def update_status(self, cid: str, status: str):
        """
        Update status for given CID.

        Args:
            cid: Correlation ID to update
            status: New status value

        Returns:
            Updated ExecutionCycle or None if CID not found
        """
        return self._cid_registry.update_status(cid, status)
