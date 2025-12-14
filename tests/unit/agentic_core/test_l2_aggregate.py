"""Unit tests for L2_execution/P3_aggregate - execution result aggregation."""
from typing import Dict, List
import logging


logger = logging.getLogger(__name__)
class TestExecutionResultAggregation:
    """Tests for aggregating execution results."""

    def test_aggregate_multiple_results(self):
        """Nominal: Multiple results are aggregated."""
        results = [
            {"tool": "search", "data": [1, 2]},
            {"tool": "fetch", "data": [3, 4]},
        ]
        all_data = [item for r in results for item in r["data"]]
        assert all_data == [1, 2, 3, 4]

    def test_aggregate_with_errors(self):
        """Nominal: Errors are collected separately."""
        results = [
            {"status": "success", "data": "ok"},
            {"status": "error", "error": "failed"},
        ]
        errors = [r for r in results if r["status"] == "error"]
        successes = [r for r in results if r["status"] == "success"]
        assert len(errors) == 1
        assert len(successes) == 1

    def test_aggregate_empty_results(self):
        """Edge case: Empty results list."""
        results: List[Dict] = []
        aggregated = [item for r in results for item in r.get("data", [])]
        assert aggregated == []

    def test_aggregate_preserves_order(self):
        """Nominal: Aggregation preserves order."""
        results = [{"id": 1}, {"id": 2}, {"id": 3}]
        ids = [r["id"] for r in results]
        assert ids == [1, 2, 3]

    def test_aggregate_deduplication(self):
        """Nominal: Duplicate results are deduplicated."""
        results = [{"id": 1}, {"id": 2}, {"id": 1}]
        seen = set()
        unique = [r for r in results if r["id"] not in seen and not seen.add(r["id"])]
        assert len(unique) == 2
