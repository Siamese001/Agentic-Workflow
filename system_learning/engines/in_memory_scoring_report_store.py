"""In-memory implementation of scoring report store.

Phase 4: Test implementation with write-once idempotency.
Provides readback for test verification.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.ports.scoring_report_store import ScoringReportStore
from system_learning.types.healing_outcome_scoring_types import ScoringReport


class InMemoryScoringReportStore(ScoringReportStore):
    """In-memory store for scoring reports.

    Simple dict-based storage keyed by content hash for write-once idempotency.
    """

    def __init__(self) -> None:
        """Initialize empty store."""
        self._reports_by_hash: dict[str, ScoringReport] = {}
        self._reports: list[ScoringReport] = []

    def write(self, report: ScoringReport) -> None:
        """Persist a scoring report with write-once idempotency.

        Args:
            report: The scoring report to persist
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryScoringReportStore.write")

        content_hash = report.content_hash()
        if content_hash not in self._reports_by_hash:
            self._reports_by_hash[content_hash] = report
            self._reports.append(report)

    def count(self) -> int:
        """Get number of stored reports.

        Returns:
            Number of reports in the store
        """
        return len(self._reports)

    def get_reports(self) -> list[ScoringReport]:
        """Get all stored reports.

        Returns:
            Copy of stored reports list
        """
        return list(self._reports)

    def clear(self) -> None:
        """Clear all stored reports."""
        self._reports.clear()
