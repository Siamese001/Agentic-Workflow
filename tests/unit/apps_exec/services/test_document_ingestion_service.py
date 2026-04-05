"""Test DocumentIngestionService functionality."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDocumentIngestionService:
    """Test DocumentIngestionService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        config = {"max_file_size_kb": 1024}
        service = DocumentIngestionService(config)
        assert service.config == config
        assert service._max_file_size_kb == 1024

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        service = DocumentIngestionService()
        assert service.config == {}
        assert service._max_file_size_kb == 512
        assert service._ingested_docs == []

    @patch("apps_exec.services.document_ingestion_service.emit_replay_key")
    @patch("apps_exec.services.document_ingestion_service.emit_determinism_digest")
    @patch("apps_exec.services.document_ingestion_service._emit_applies_guardrail")
    @patch("apps_exec.services.document_ingestion_service._emit_snapshots_state")
    def test_init_emits_lifecycle_events(self, mock_state, mock_guardrail, mock_digest, mock_replay):
        """Test that initialization emits all lifecycle events."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        DocumentIngestionService()
        mock_replay.assert_called_once_with("doc_ingestion", "init")
        mock_digest.assert_called_once_with("doc_ingestion", "init")
        mock_guardrail.assert_called_once_with("p0", "doc_ingestion", "service_init")
        mock_state.assert_called_once_with("p0", "doc_ingestion", "service_state")

    def test_supported_extensions(self):
        """Test supported file extensions."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        assert ".md" in DocumentIngestionService.SUPPORTED_EXTENSIONS
        assert ".txt" in DocumentIngestionService.SUPPORTED_EXTENSIONS
        assert ".json" in DocumentIngestionService.SUPPORTED_EXTENSIONS
        assert ".rst" in DocumentIngestionService.SUPPORTED_EXTENSIONS
        assert ".adoc" in DocumentIngestionService.SUPPORTED_EXTENSIONS

    def test_ingest_directory_empty(self):
        """Test ingesting from empty directory."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        with TemporaryDirectory() as tmpdir:
            service = DocumentIngestionService()
            docs = service.ingest_directory(tmpdir)

            assert docs == []

    def test_ingest_directory_with_supported_files(self):
        """Test ingesting directory with supported files."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("# Test", encoding="utf-8")
            (Path(tmpdir) / "test.txt").write_text("Test content", encoding="utf-8")

            service = DocumentIngestionService()
            docs = service.ingest_directory(tmpdir)

            assert len(docs) == 2

    def test_ingest_directory_with_unsupported_files(self):
        """Test ingesting directory filters unsupported files."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.pdf").write_text("PDF content", encoding="utf-8")
            (Path(tmpdir) / "test.docx").write_text("DOCX content", encoding="utf-8")

            service = DocumentIngestionService()
            docs = service.ingest_directory(tmpdir)

            assert len(docs) == 0

    def test_ingest_directory_custom_extensions(self):
        """Test ingesting with custom file extensions."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("# Test", encoding="utf-8")
            (Path(tmpdir) / "test.txt").write_text("Test content", encoding="utf-8")

            service = DocumentIngestionService()
            docs = service.ingest_directory(tmpdir, extensions={".md"})

            assert len(docs) == 1

    def test_ingest_directory_nonexistent(self):
        """Test ingesting from nonexistent directory raises ValueError."""
        from apps_exec.services.document_ingestion_service import DocumentIngestionService

        service = DocumentIngestionService()
        # Nonexistent directory should raise ValueError
        with pytest.raises(ValueError, match="Directory does not exist"):
            service.ingest_directory("/nonexistent/directory")
