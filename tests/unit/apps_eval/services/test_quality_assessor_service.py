"""Test QualityAssessorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQualityAssessorService:
    """Test QualityAssessorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        config = {"threshold": 0.8}
        service = QualityAssessorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        service = QualityAssessorService()
        assert service.config == {}

    @patch("apps_eval.services.quality_assessor_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        QualityAssessorService()
        mock_emit.assert_called_once_with("p4", "quality_assessor", "init")

    def test_assess_quality(self):
        """Test assessing output quality."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        service = QualityAssessorService()
        output = {"text": "Sample output", "metrics": {"accuracy": 0.9}}
        result = service.assess_quality(output)

        assert result["quality_score"] == 0.9
        assert "dimensions" in result

    def test_assess_quality_empty_output(self):
        """Test assessing quality with empty output (edge case)."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        service = QualityAssessorService()
        result = service.assess_quality({})

        assert result["quality_score"] == 0.9
        assert "dimensions" in result

    def test_assess_quality_none_output(self):
        """Test assessing quality with None output (edge case)."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        service = QualityAssessorService()
        result = service.assess_quality(None)  # type: ignore[arg-type]

        assert result["quality_score"] == 0.9

    def test_assess_quality_large_output(self):
        """Test assessing quality with large output (edge case)."""
        from apps_eval.services.quality_assessor_service import QualityAssessorService

        service = QualityAssessorService()
        large_output = {"data": "x" * 10000}
        result = service.assess_quality(large_output)

        assert result["quality_score"] == 0.9
