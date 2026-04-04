"""ADG-driven tests for system_learning/ports/scoring_report_store.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

class TestScoringReportStore:

    def test_importable(self):
        from system_learning.ports.scoring_report_store import ScoringReportStore
        assert ScoringReportStore is not None

    def test_has_write(self):
        assert hasattr(ScoringReportStore, 'write')

    def test_concrete_implementor(self):

        class ConcreteScoringReportStore:

            def __init__(self):
                self._reports = []

            def write(self, report) -> None:
                self._reports.append(report)
        store = ConcreteScoringReportStore()
        assert callable(store.write)
        store.write({'score': 0.9})
        assert len(store._reports) == 1
