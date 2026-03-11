"""Healing Outcome Intake Store Protocol - persist-only interface."""

from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class HealingOutcomeIntakeStore:
    """Protocol for persisting healing outcome intake records.

    This is a persist-only interface - no reads or queries required
    for the basic intake functionality.
    """

    def write(self, record: HealingOutcomeIntakeRecord) -> None:
        """Persist a healing outcome intake record.

        Args:
            record: The immutable intake record to persist

        Raises:
            IOError: If the write operation fails
        """
        raise NotImplementedError

    def get_records(self) -> list:
        """Return all persisted records for pipeline consumption.

        Returns:
            List of all persisted HealingOutcomeIntakeRecord instances
        """
        raise NotImplementedError
