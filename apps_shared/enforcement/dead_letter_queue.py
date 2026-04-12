"""Dead Letter Queue - Stub implementation for test compatibility."""

from enum import Enum
from typing import Any


class FailureReason(Enum):
    """Reason for failure."""

    PROCESSING_ERROR = "processing_error"
    TIMEOUT = "timeout"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    BULKHEAD_REJECTED = "bulkhead_rejected"


class DeadLetterQueue:
    """Stub dead letter queue."""

    def __init__(self):
        self._failed_envelopes: list[dict[str, Any]] = []

    async def add_failed_envelope(
        self, envelope: Any, reason: FailureReason, source: str, error: str
    ) -> None:
        """Add failed envelope to DLQ."""
        self._failed_envelopes.append(
            {
                "envelope": envelope,
                "reason": reason,
                "source": source,
                "error": error,
            }
        )

    async def get_failed_envelopes(self) -> list[dict[str, Any]]:
        """Get all failed envelopes."""
        return self._failed_envelopes.copy()


_dlq: DeadLetterQueue | None = None


async def get_dead_letter_queue() -> DeadLetterQueue:
    """Get global dead letter queue instance."""
    global _dlq
    if _dlq is None:
        _dlq = DeadLetterQueue()
    return _dlq


__all__ = ["DeadLetterQueue", "FailureReason", "get_dead_letter_queue"]
