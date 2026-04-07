"""Intake Clerk - Unified Document Ingestion Interface.

The Intake Clerk serves as the unified entry point for all document ingestion
in Pipeline B. It handles content type detection, modality classification,
and routing to appropriate extractors with proper metadata generation.
"""

import logging
import time
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

from .modality_types import ContentMetadata, ContentType, DocumentModality, IngestionResult
from .visual_detector import VisualDetector

# Import existing document loaders
try:
    from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
    from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
    from agentic_core.knowledge.document_loaders.pdf_document_loader_config import PDFDocumentLoader
    from agentic_core.knowledge.document_loaders.text_document_loader_config import TextDocumentLoader
except ImportError as e:
    logging.getLogger(__name__).warning(f"Document loader import failed: {e}")
    TextDocumentLoader = None
    PDFDocumentLoader = None
    HTMLDocumentLoader = None
    CSVDocumentLoader = None

log = logging.getLogger(__name__)


class IntakeClerk:
    """Unified intake clerk for document ingestion and processing.

    The Intake Clerk implements Pipeline B Step 1: INTAKE & MODALITY DETECT.
    It provides a single interface for ingesting documents of various types,
    automatically detecting content modalities and routing to appropriate
    extractors with comprehensive metadata generation.
    """

    def __init__(self):
        """Initialize the intake clerk with visual detector and loaders."""
        self.visual_detector = VisualDetector()
        self._loaders: dict[ContentType, callable] = {}
        self._setup_loaders()

    def _setup_loaders(self):
        """Setup document loaders for different content types."""
        if TextDocumentLoader:
            self._loaders[ContentType.TEXT] = TextDocumentLoader.load_file
            self._loaders[ContentType.MARKDOWN] = TextDocumentLoader.load_file
        if PDFDocumentLoader:
            self._loaders[ContentType.PDF] = PDFDocumentLoader.load_file
        if HTMLDocumentLoader:
            self._loaders[ContentType.HTML] = HTMLDocumentLoader.load_file
        if CSVDocumentLoader:
            # CSV loader returns list of dicts, need to convert to string
            def csv_loader_wrapper(file_path):
                records = CSVDocumentLoader.load(file_path)
                return str(records)  # Convert to string for processing
            self._loaders[ContentType.CSV] = csv_loader_wrapper

    def ingest_document(self, file_path: str | Path) -> IngestionResult:
        """Ingest a single document with full processing pipeline.

        Args:
            file_path: Path to the document to ingest

        Returns:
            IngestionResult with content, metadata, and processing status
        """
        start_time = time.time()
        file_path = Path(file_path)

        trace_id = f"ingest_{file_path.stem}_{int(start_time)}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L3_ORCHESTRATION, "IntakeClerk.ingest_document",
        )

        try:
            # Validate file exists and is accessible
            if not file_path.exists():
                return IngestionResult(
                    success=False,
                    error_message=f"File not found: {file_path}",
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            if not file_path.is_file():
                return IngestionResult(
                    success=False,
                    error_message=f"Path is not a file: {file_path}",
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            # Extract content using appropriate loader
            content_result = self._extract_content(file_path)
            if not content_result.success:
                return content_result

            # Generate comprehensive metadata
            metadata = self.visual_detector.extract_metadata(file_path, content_result.content)

            processing_time = (time.time() - start_time) * 1000

            return IngestionResult(
                success=True,
                content=content_result.content,
                metadata=metadata,
                processing_time_ms=processing_time,
                warnings=content_result.warnings,
            )

        except Exception as e:
            log.error(f"Document ingestion failed for {file_path}: {e}")
            return IngestionResult(
                success=False,
                error_message=f"Ingestion failed: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def ingest_batch(self, file_paths: list[str | Path]) -> list[IngestionResult]:
        """Ingest multiple documents in batch.

        Args:
            file_paths: List of file paths to ingest

        Returns:
            List of IngestionResult objects
        """
        results = []
        for file_path in file_paths:
            result = self.ingest_document(file_path)
            results.append(result)

        log.info(f"Batch ingestion completed: {len(results)} files processed")
        success_count = sum(1 for r in results if r.success)
        log.info(f"Success rate: {success_count}/{len(results)}")

        return results

    def detect_modality(self, file_path: str | Path, content: str | None = None) -> DocumentModality:
        """Detect document modality for routing decisions.

        Args:
            file_path: Path to the document
            content: Optional pre-loaded content

        Returns:
            DocumentModality classification
        """
        file_path = Path(file_path)
        return self.visual_detector.detect_modality(file_path, content)

    def extract_metadata(self, file_path: str | Path, content: str | None = None) -> ContentMetadata:
        """Extract comprehensive metadata from document.

        Args:
            file_path: Path to the document
            content: Optional pre-loaded content

        Returns:
            ContentMetadata with extracted information
        """
        file_path = Path(file_path)
        return self.visual_detector.extract_metadata(file_path, content)

    def _extract_content(self, file_path: Path) -> IngestionResult:
        """Extract content using appropriate document loader.

        Args:
            file_path: Path to the document

        Returns:
            IngestionResult with extracted content
        """
        start_time = time.time()

        try:
            # Detect content type
            content_type = self.visual_detector._detect_content_type(file_path)

            # Get appropriate loader
            loader = self._loaders.get(content_type)
            if loader is None:
                return IngestionResult(
                    success=False,
                    error_message=f"No loader available for content type: {content_type.value}",
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            # Extract content
            content = loader(file_path)

            if not content:
                return IngestionResult(
                    success=False,
                    error_message="No content extracted from document",
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

            processing_time = (time.time() - start_time) * 1000

            # Check for potential issues
            warnings = []
            if len(content) < 10:
                warnings.append("Document appears to be very short")
            elif len(content) > 1000000:  # 1MB of text
                warnings.append("Document is very large, may impact processing")

            return IngestionResult(
                success=True,
                content=content,
                processing_time_ms=processing_time,
                warnings=warnings,
            )

        except Exception as e:
            log.error(f"Content extraction failed for {file_path}: {e}")
            return IngestionResult(
                success=False,
                error_message=f"Content extraction failed: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def get_supported_types(self) -> list[ContentType]:
        """Get list of supported content types.

        Returns:
            List of supported ContentType values
        """
        return list(self._loaders.keys())

    def register_loader(self, content_type: ContentType, loader_func: callable):
        """Register a custom loader for a content type.

        Args:
            content_type: The content type this loader handles
            loader_func: Function that takes a Path and returns content string
        """
        self._loaders[content_type] = loader_func
        log.info(f"Registered custom loader for {content_type.value}")

    def get_ingestion_stats(self, results: list[IngestionResult]) -> dict[str, int]:
        """Get statistics for a batch of ingestion results.

        Args:
            results: List of IngestionResult objects

        Returns:
            Dictionary with ingestion statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        # Modality distribution
        modality_counts = {}
        for result in results:
            if result.success and result.metadata:
                modality = result.metadata.modality.value
                modality_counts[modality] = modality_counts.get(modality, 0) + 1

        # Content type distribution
        content_type_counts = {}
        for result in results:
            if result.success and result.metadata:
                content_type = result.metadata.content_type.value
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1

        # Processing time stats
        processing_times = [r.processing_time_ms for r in results if r.processing_time_ms is not None]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0

        return {
            "total_documents": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "modality_distribution": modality_counts,
            "content_type_distribution": content_type_counts,
            "avg_processing_time_ms": avg_time,
            "total_processing_time_ms": sum(processing_times),
        }


# Global instance for convenience
_global_intake_clerk: IntakeClerk | None = None


def get_intake_clerk() -> IntakeClerk:
    """Get or create the global intake clerk instance."""
    global _global_intake_clerk
    if _global_intake_clerk is None:
        _global_intake_clerk = IntakeClerk()
    return _global_intake_clerk


def ingest_document(file_path: str | Path) -> IngestionResult:
    """Convenience function to ingest a single document."""
    return get_intake_clerk().ingest_document(file_path)


def ingest_batch(file_paths: list[str | Path]) -> list[IngestionResult]:
    """Convenience function to ingest multiple documents."""
    return get_intake_clerk().ingest_batch(file_paths)
