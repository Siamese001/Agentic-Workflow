"""Test ResultAggregatorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResultAggregatorService:
    """Test ResultAggregatorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        config = {"max_results": 1000}
        service = ResultAggregatorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        service = ResultAggregatorService()
        assert service.config == {}

    @patch("apps_eval.services.result_aggregator_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        ResultAggregatorService()
        mock_emit.assert_called_once_with("p4", "result_aggregator", "init")

    def test_aggregate_results(self):
        """Test aggregating test results."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        service = ResultAggregatorService()
        results = [
            {"test_id": "test_1", "status": "passed"},
            {"test_id": "test_2", "status": "passed"},
            {"test_id": "test_3", "status": "passed"},
        ]
        aggregated = service.aggregate_results(results)

        assert aggregated["total"] == 3
        assert aggregated["passed"] == 3
        assert aggregated["failed"] == 0

    def test_aggregate_results_empty(self):
        """Test aggregating empty results list."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        service = ResultAggregatorService()
        aggregated = service.aggregate_results([])

        assert aggregated["total"] == 0
        assert aggregated["passed"] == 0
        assert aggregated["failed"] == 0

    def test_aggregate_results_large_list(self):
        """Test aggregating large results list (edge case)."""
        from apps_eval.services.result_aggregator_service import ResultAggregatorService

        service = ResultAggregatorService()
        results = [{"test_id": f"test_{i}", "status": "passed"} for i in range(1000)]
        aggregated = service.aggregate_results(results)

        assert aggregated["total"] == 1000
