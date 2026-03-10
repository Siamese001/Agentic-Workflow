"""Port for persisting scoring reports.

Phase 3: Optional store for offline evaluator pipeline integration.
Persist-only protocol; no reads required.
"""

from __future__ import annotations

from typing import Protocol

from system_learning.types.healing_outcome_scoring_types import ScoringReport


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class ScoringReportStore(Protocol):
    """Protocol for persisting scoring reports.

    Write-only interface for shadow mode evaluation.
    """

    def write(self, report: ScoringReport) -> None:
        """Persist a scoring report.

        Args:
            report: The scoring report to persist
        """
        ...
