from __future__ import annotations
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class NonMonotonicRetryViolation(Exception):
    """Raised when a retry count is not incremented monotonically."""

class MonotonicReentrancyEnforcer:
    """
    Ensures that the healing retry_count is strictly monotonic and persistent.

    This enforcer enforces Guarantee #19 by managing the retry count in L4 state,
    making it immune to agent manipulation or system restarts. The `_tier_escalate`
    function, which calls this, must be a pure function with no side-effects other
    than returning the next healing tier.
    """

    def __init__(self):
        self._persistent_retry_counts: dict[str, int] = {}

    def get_and_increment_retry_count(self, trace_id: str) -> int:
        """
        Retrieves the current retry count for a trace and increments it atomically.

        This is the only way to get a valid retry count. The count is persisted
        in L4, ensuring it survives agent restarts or other interruptions.

        Args:
            trace_id: The unique identifier for the failure trace.

        Returns:
            The new, incremented retry count.
        """
        current_count = self._persistent_retry_counts.get(trace_id, 0)
        new_count = current_count + 1
        self._persistent_retry_counts[trace_id] = new_count
        return new_count

    def validate_monotonicity(self, trace_id: str, proposed_count: int) -> None:
        """
        Validates that a proposed retry count is monotonically correct.

        This would be used by the tier escalation logic to assert that the count
        it received is the one it expected, preventing state desynchronization.

        Args:
            trace_id: The unique identifier for the failure trace.
            proposed_count: The retry count being used in the current operation.

        Raises:
            NonMonotonicRetryViolation: If the proposed count is not exactly one
                                        greater than the persisted count.
        """
        expected_next_count = self._persistent_retry_counts.get(trace_id, 0)
        if proposed_count != expected_next_count:
            raise NonMonotonicRetryViolation(f"Invalid retry count for trace '{trace_id}'. Expected {expected_next_count}, got {proposed_count}.")
