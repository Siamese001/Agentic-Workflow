"""Healing Outcome Intake Store Protocol - persist-only interface."""
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

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
