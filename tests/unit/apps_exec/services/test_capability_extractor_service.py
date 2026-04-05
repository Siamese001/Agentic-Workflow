"""Test CapabilityExtractorService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCapabilityExtractorService:
    """Test CapabilityExtractorService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        config = {"extraction_mode": "full"}
        service = CapabilityExtractorService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        service = CapabilityExtractorService()
        assert service.config == {}

    @patch("apps_exec.services.capability_extractor_service._emit_records_telemetry_event")
    def test_init_emits_telemetry(self, mock_emit):
        """Test that initialization emits telemetry event."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        CapabilityExtractorService()
        mock_emit.assert_called_once_with("p4", "capability_extractor", "init")

    @patch("apps_exec.services.capability_extractor_service._emit_stores_embedding")
    def test_extract_capabilities(self, mock_emit):
        """Test extracting capabilities from document."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        service = CapabilityExtractorService()
        document = {"title": "Resume", "content": "Skills: Python, AWS"}
        capabilities = service.extract_capabilities(document)

        assert capabilities == []
        mock_emit.assert_called_once_with("p4", "capability_extractor", "doc_embedding")

    def test_extract_capabilities_empty_document(self):
        """Test extracting from empty document (edge case)."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        with patch("apps_exec.services.capability_extractor_service._emit_stores_embedding"):
            service = CapabilityExtractorService()
            capabilities = service.extract_capabilities({})

            assert capabilities == []

    def test_extract_capabilities_none_document(self):
        """Test extracting from None document (edge case)."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        with patch("apps_exec.services.capability_extractor_service._emit_stores_embedding"):
            service = CapabilityExtractorService()
            capabilities = service.extract_capabilities(None)  # type: ignore[arg-type]

            assert capabilities == []

    def test_get_extracted_capabilities(self):
        """Test getting extracted capabilities."""
        from apps_exec.services.capability_extractor_service import CapabilityExtractorService

        service = CapabilityExtractorService()
        capabilities = service.get_extracted_capabilities()

        assert capabilities == []
