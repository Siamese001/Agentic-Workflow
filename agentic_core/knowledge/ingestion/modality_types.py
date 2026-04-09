"""Document Modality Types.

Defines types for content detection and routing in the ingestion pipeline.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


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


class IngestionSecurityError(ValueError):
    """Raised when ContentMetadata is missing mandatory security fields at commit time."""


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
    language: str | None = None
    encoding: str = "utf-8"
    checksum: str | None = None
    parent_id: str | None = None
    source_identifier: str | None = None
    extracted_at: str | None = None
    acl_policy_ref: Optional[str] = None
    tenant_id: Optional[str] = None
    source_trust_level: Optional[str] = None
    classification_label: Optional[str] = None
    ingestion_authorized_by: Optional[str] = None
    scope_boundary: Optional[str] = None

    _REQUIRED_SECURITY_FIELDS: tuple = (
        "acl_policy_ref",
        "tenant_id",
        "source_trust_level",
        "classification_label",
        "ingestion_authorized_by",
        "scope_boundary",
    )

    def validate_security_fields(self) -> None:
        """Enforce that all 6 security fields are populated before L4 commit.

        Raises:
            IngestionSecurityError: if any mandatory security field is None or empty.
        """
        missing = [f for f in self._REQUIRED_SECURITY_FIELDS if not (getattr(self, f, None) or "").strip()]
        if missing:
            raise IngestionSecurityError(
                f"ContentMetadata is missing mandatory security fields before L4 commit: {missing}. "
                "All ingestion paths must supply acl_policy_ref, tenant_id, source_trust_level, "
                "classification_label, ingestion_authorized_by, and scope_boundary."
            )

    def to_dict(self) -> dict[str, Any]:
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
            "acl_policy_ref": self.acl_policy_ref,
            "tenant_id": self.tenant_id,
            "source_trust_level": self.source_trust_level,
            "classification_label": self.classification_label,
            "ingestion_authorized_by": self.ingestion_authorized_by,
            "scope_boundary": self.scope_boundary,
        }


@dataclass
class IngestionResult:
    """Result of document ingestion process."""

    success: bool
    content: str | None = None
    metadata: ContentMetadata | None = None
    error_message: str | None = None
    processing_time_ms: float | None = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
