"""Test ContentSynthesizerService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestContentSynthesizerService:
    """Test ContentSynthesizerService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        config = {"synthesis_mode": "comprehensive"}
        service = ContentSynthesizerService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        service = ContentSynthesizerService()
        assert service.config == {}

    @patch("apps_exec.services.content_synthesizer_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        ContentSynthesizerService()
        mock_emit.assert_called_once_with("p4", "content_synthesizer", "init")

    def test_synthesize_content(self):
        """Test synthesizing content from documents."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        service = ContentSynthesizerService()
        documents = [
            {"title": "Doc1", "content": "Content 1"},
            {"title": "Doc2", "content": "Content 2"}
        ]
        result = service.synthesize_content(documents)

        assert result["synthesized"] is True
        assert result["document_count"] == 2

    def test_synthesize_content_empty_list(self):
        """Test synthesizing with empty document list (edge case)."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        service = ContentSynthesizerService()
        result = service.synthesize_content([])

        assert result["synthesized"] is True
        assert result["document_count"] == 0

    def test_synthesize_content_large_list(self):
        """Test synthesizing with large document list (edge case)."""
        from apps_exec.services.content_synthesizer_service import ContentSynthesizerService

        service = ContentSynthesizerService()
        documents = [{"title": f"Doc{i}", "content": f"Content {i}"} for i in range(100)]
        result = service.synthesize_content(documents)

        assert result["document_count"] == 100
