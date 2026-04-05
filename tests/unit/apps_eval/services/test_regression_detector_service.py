"""Test RegressionDetectorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRegressionDetectorService:
    """Test RegressionDetectorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        config = {"threshold": 0.1}
        service = RegressionDetectorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        service = RegressionDetectorService()
        assert service.config == {}

    @patch("apps_eval.services.regression_detector_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        RegressionDetectorService()
        mock_emit.assert_called_once_with("p4", "regression_detector", "init")

    def test_detect_regressions(self):
        """Test detecting regressions."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        service = RegressionDetectorService()
        current = {"metric1": 0.85, "metric2": 0.9}
        baseline = {"metric1": 0.9, "metric2": 0.95}
        regressions = service.detect_regressions(current, baseline)

        assert regressions == []

    def test_detect_regressions_empty_inputs(self):
        """Test detecting regressions with empty inputs (edge case)."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        service = RegressionDetectorService()
        regressions = service.detect_regressions({}, {})

        assert regressions == []

    def test_detect_regressions_none_inputs(self):
        """Test detecting regressions with None inputs (edge case)."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        service = RegressionDetectorService()
        regressions = service.detect_regressions(None, None)  # type: ignore[arg-type]

        assert regressions == []

    def test_detect_regressions_mismatched_keys(self):
        """Test detecting regressions with mismatched keys (edge case)."""
        from apps_eval.services.regression_detector_service import RegressionDetectorService

        service = RegressionDetectorService()
        current = {"metric1": 0.85}
        baseline = {"metric2": 0.9}
        regressions = service.detect_regressions(current, baseline)

        assert regressions == []
