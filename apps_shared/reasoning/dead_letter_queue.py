"""Dead Letter Queue - Re-export from enforcement for reasoning compatibility."""
from apps_shared.enforcement.dead_letter_queue import (
    DeadLetterQueue,
    FailureReason,
    get_dead_letter_queue,
)

__all__ = ["DeadLetterQueue", "FailureReason", "get_dead_letter_queue"]
