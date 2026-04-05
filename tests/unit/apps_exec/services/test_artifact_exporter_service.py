"""Test ArtifactExporterService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestArtifactExporterService:
    """Test ArtifactExporterService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        config = {"output_format": "json"}
        service = ArtifactExporterService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        service = ArtifactExporterService()
        assert service.config == {}

    @patch("apps_exec.services.artifact_exporter_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        ArtifactExporterService()
        mock_emit.assert_called_once_with("p4", "artifact_exporter", "init")

    def test_export_artifact(self):
        """Test exporting brief artifact."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        service = ArtifactExporterService()
        brief = {"title": "Test Brief", "content": "Test content"}
        result = service.export_artifact(brief, "/output/dir")

        assert result["exported"] is True
        assert result["output_dir"] == "/output/dir"

    def test_export_artifact_empty_brief(self):
        """Test exporting empty brief (edge case)."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        service = ArtifactExporterService()
        result = service.export_artifact({}, "/output/dir")

        assert result["exported"] is True

    def test_export_artifact_none_brief(self):
        """Test exporting None brief (edge case)."""
        from apps_exec.services.artifact_exporter_service import ArtifactExporterService

        service = ArtifactExporterService()
        result = service.export_artifact(None, "/output/dir")  # type: ignore[arg-type]

        assert result["exported"] is True
