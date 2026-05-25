"""Port for persisting scoring reports.

Phase 3: Optional store for offline evaluator pipeline integration.
Persist-only protocol; no reads required.
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.L6_system_learning.types.healing_outcome_scoring_types import ScoringReport


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
