"""Port for persisting scoring reports.

Phase 3: Optional store for offline evaluator pipeline integration.
Persist-only protocol; no reads required.
"""
from __future__ import annotations
from typing import Protocol
from system_learning.types.healing_outcome_scoring_types import ScoringReport
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

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
