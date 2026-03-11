"""In-memory implementation of HealingOutcomeIntakeStore for testing."""

from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
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

class InMemoryHealingOutcomeIntakeStore(HealingOutcomeIntakeStore):
    """In-memory store implementation for testing and development.

    Stores records in a list and provides readback for assertions.
    """

    def __init__(self) -> None:
        """Initialize empty record store."""
        self._records: list[HealingOutcomeIntakeRecord] = []

    def write(self, record: HealingOutcomeIntakeRecord) -> None:
        """Store a record in memory.

        Args:
            record: The record to store
        """
        self._records.append(record)

    def get_records(self) -> list[HealingOutcomeIntakeRecord]:
        """Get all stored records for test assertions.

        Returns:
            List of all records in insertion order
        """
        return list(self._records)

    def clear(self) -> None:
        """Clear all stored records (useful for test isolation)."""
        self._records.clear()

    def count(self) -> int:
        """Get the number of stored records.

        Returns:
            Number of records
        """
        return len(self._records)
