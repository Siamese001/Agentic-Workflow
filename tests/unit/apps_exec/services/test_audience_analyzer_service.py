"""Test AudienceAnalyzerService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAudienceAnalyzerService:
    """Test AudienceAnalyzerService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        config = {"default_persona": "recruiter"}
        service = AudienceAnalyzerService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        service = AudienceAnalyzerService()
        assert service.config == {}

    @patch("apps_exec.services.audience_analyzer_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        AudienceAnalyzerService()
        mock_emit.assert_called_once_with("p4", "audience_analyzer", "init")

    def test_analyze_audience(self):
        """Test analyzing audience characteristics."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        service = AudienceAnalyzerService()
        result = service.analyze_audience("recruiter")

        assert result["persona_id"] == "recruiter"
        assert "characteristics" in result

    def test_analyze_audience_empty_persona(self):
        """Test analyzing with empty persona ID (edge case)."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        service = AudienceAnalyzerService()
        result = service.analyze_audience("")

        assert result["persona_id"] == ""

    def test_analyze_audience_long_persona(self):
        """Test analyzing with long persona ID (edge case)."""
        from apps_exec.services.audience_analyzer_service import AudienceAnalyzerService

        service = AudienceAnalyzerService()
        long_id = "x" * 1000
        result = service.analyze_audience(long_id)

        assert result["persona_id"] == long_id
