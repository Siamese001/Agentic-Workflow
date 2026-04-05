"""
Document Ingestion Service — apps_exec

Ingests and processes source documents for executive brief generation.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class DocumentIngestionService:
    """Service for ingesting and processing source documents."""

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".rst", ".adoc"}

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the document ingestion service."""
        self.config = config or {}
        self._ingested_docs: list[dict[str, Any]] = []
        self._max_file_size_kb = self.config.get("max_file_size_kb", 512)

        # Lifecycle trace emission
        emit_replay_key("doc_ingestion", "init")
        emit_determinism_digest("doc_ingestion", "init")
        _emit_applies_guardrail("p0", "doc_ingestion", "service_init")
        _emit_snapshots_state("p0", "doc_ingestion", "service_state")

    def ingest_directory(
        self,
        directory: str,
        recursive: bool = True,
        extensions: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Ingest all documents from a directory.

        Args:
            directory: Path to directory
            recursive: Whether to recurse into subdirectories
            extensions: File extensions to include

        Returns:
            List of ingested document metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DocumentIngestionService.ingest_directory"
        )
        _emit_routes_to_capability("p2", "doc_ingestion", "filesystem_access")
        _emit_validates_capability("p2", "doc_ingestion", "read_permissions")
        _emit_records_telemetry_event("p4", "doc_ingestion", "ingest_start")

        extensions = extensions or self.SUPPORTED_EXTENSIONS
        dir_path = Path(directory)

        if not dir_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        ingested: list[dict[str, Any]] = []
        pattern = "**/*" if recursive else "*"

        for ext in extensions:
            for file_path in dir_path.glob(f"{pattern}{ext}"):
                if file_path.is_file():
                    doc = self._ingest_file(file_path)
                    if doc:
                        ingested.append(doc)

        self._ingested_docs.extend(ingested)
        _log.info("Ingested %d documents from %s", len(ingested), directory)
        _emit_records_telemetry_event("p4", "doc_ingestion", f"ingest_complete:{len(ingested)}")

        return ingested

    def ingest_file(self, file_path: str) -> dict[str, Any] | None:
        """Ingest a single document file.

        Args:
            file_path: Path to file

        Returns:
            Document metadata or None if ingestion failed
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "DocumentIngestionService.ingest_file"
        )

        path = Path(file_path)
        if not path.exists():
            _log.error("File does not exist: %s", file_path)
            return None

        return self._ingest_file(path)

    def _ingest_file(self, path: Path) -> dict[str, Any] | None:
        """Internal method to ingest a file."""
        # Check file size
        size_kb = path.stat().st_size / 1024
        if size_kb > self._max_file_size_kb:
            _log.warning("File exceeds max size (%d KB): %s", self._max_file_size_kb, path)
            _emit_records_telemetry_event("p4", "doc_ingestion", f"size_exceeded:{path.name}")
            return None

        try:
            content = path.read_text(encoding="utf-8")
            doc = {
                "doc_id": path.stem,
                "path": str(path),
                "extension": path.suffix,
                "size_kb": size_kb,
                "content": content,
                "word_count": len(content.split()),
            }
            _emit_records_telemetry_event("p4", "doc_ingestion", f"file_ingested:{path.name}")
            return doc
        except UnicodeDecodeError:
            _log.error("Failed to decode file: %s", path)
            _emit_records_telemetry_event("p4", "doc_ingestion", f"decode_error:{path.name}")
            return None

    def get_ingested_docs(self) -> list[dict[str, Any]]:
        """Get all ingested documents."""
        return self._ingested_docs.copy()

    def clear_cache(self) -> None:
        """Clear the ingested document cache."""
        self._ingested_docs.clear()
        _emit_records_telemetry_event("p4", "doc_ingestion", "cache_cleared")
