"""Document Modality Types.

Defines types for content detection and routing in the ingestion pipeline.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class ContentType(Enum):
    """Content type enumeration for document classification."""
    TEXT = "text"
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    CODE = "code"
    UNKNOWN = "unknown"


class DocumentModality(Enum):
    """Document modality classification."""
    TEXT_ONLY = "text_only"
    VISUAL_HEAVY = "visual_heavy"
    MIXED_MODAL = "mixed_modal"
    TABULAR_DATA = "tabular_data"
    STRUCTURED_TEXT = "structured_text"
    SEMI_STRUCTURED = "semi_structured"
    INCIDENT_TRACE = "incident_trace"
    POLICY_DOCUMENT = "policy_document"
    CODE_BASE = "code_base"
    UNKNOWN = "unknown"


@dataclass
class ContentMetadata:
    """Metadata extracted from document content."""
    file_path: str
    content_type: ContentType
    modality: DocumentModality
    file_size_bytes: int
    estimated_tokens: int
    has_tables: bool = False
    has_images: bool = False
    has_code_blocks: bool = False
    has_headings: bool = False
    language: Optional[str] = None
    encoding: str = "utf-8"
    checksum: Optional[str] = None
    parent_id: Optional[str] = None
    source_identifier: Optional[str] = None
    extracted_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": self.file_path,
            "content_type": self.content_type.value,
            "modality": self.modality.value,
            "file_size_bytes": self.file_size_bytes,
            "estimated_tokens": self.estimated_tokens,
            "has_tables": self.has_tables,
            "has_images": self.has_images,
            "has_code_blocks": self.has_code_blocks,
            "has_headings": self.has_headings,
            "language": self.language,
            "encoding": self.encoding,
            "checksum": self.checksum,
            "parent_id": self.parent_id,
            "source_identifier": self.source_identifier,
            "extracted_at": self.extracted_at,
        }


@dataclass
class IngestionResult:
    """Result of document ingestion process."""
    success: bool
    content: Optional[str] = None
    metadata: Optional[ContentMetadata] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    warnings: list[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
