"""Test StyleValidatorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStyleValidatorService:
    """Test StyleValidatorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        config = {"strict_mode": True}
        service = StyleValidatorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        service = StyleValidatorService()
        assert service.config == {}

    @patch("apps_exec.services.style_validator_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        StyleValidatorService()
        mock_emit.assert_called_once_with("p4", "style_validator", "init")

    def test_validate_style(self):
        """Test validating content style."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        service = StyleValidatorService()
        result = service.validate_style("Test content", "recruiter")

        assert result["valid"] is True
        assert result["violations"] == []

    def test_validate_style_empty_content(self):
        """Test validating with empty content (edge case)."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        service = StyleValidatorService()
        result = service.validate_style("", "recruiter")

        assert result["valid"] is True

    def test_validate_style_empty_persona(self):
        """Test validating with empty persona (edge case)."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        service = StyleValidatorService()
        result = service.validate_style("Test content", "")

        assert result["valid"] is True

    def test_validate_style_long_content(self):
        """Test validating with long content (edge case)."""
        from apps_exec.services.style_validator_service import StyleValidatorService

        service = StyleValidatorService()
        long_content = "x" * 10000
        result = service.validate_style(long_content, "recruiter")

        assert result["valid"] is True
