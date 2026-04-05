"""Test BenchmarkRunnerService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBenchmarkRunnerService:
    """Test BenchmarkRunnerService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        config = {"timeout": 300}
        service = BenchmarkRunnerService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        service = BenchmarkRunnerService()
        assert service.config == {}

    @patch("apps_eval.services.benchmark_runner_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        BenchmarkRunnerService()
        mock_emit.assert_called_once_with("p4", "benchmark_runner", "init")

    def test_run_benchmark(self):
        """Test running a benchmark suite."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        service = BenchmarkRunnerService()
        result = service.run_benchmark("suite_123")

        assert result["suite_id"] == "suite_123"
        assert result["status"] == "completed"
        assert result["score"] == 0.85

    def test_run_benchmark_with_empty_suite_id(self):
        """Test running benchmark with empty suite ID (edge case)."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        service = BenchmarkRunnerService()
        result = service.run_benchmark("")

        assert result["suite_id"] == ""
        assert result["status"] == "completed"

    def test_run_benchmark_with_long_suite_id(self):
        """Test running benchmark with long suite ID (edge case)."""
        from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService

        service = BenchmarkRunnerService()
        long_id = "x" * 1000
        result = service.run_benchmark(long_id)

        assert result["suite_id"] == long_id
