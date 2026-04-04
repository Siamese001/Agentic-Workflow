"""Canonical Unit Types.

Defines types and enums for canonical raw unit management.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class CanonicalUnitType(Enum):
    """Type of canonical unit."""
    DOCUMENT = "document"
    CHUNK = "chunk"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    IMAGE = "image"
    METADATA = "metadata"


class CanonicalUnitStatus(Enum):
    """Status of canonical unit."""
    ACTIVE = "active"
    TOMBSTONED = "tombstoned"
    SUPERSEDED = "superseded"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class CanonicalIdentifier:
    """Canonical identifier for units with version tracking."""
    unit_id: str
    version: int
    checksum: str
    created_at: datetime

    def __str__(self) -> str:
        return f"{self.unit_id}:v{self.version}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "unit_id": self.unit_id,
            "version": self.version,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CanonicalLineage:
    """Lineage information for canonical units."""
    parent_id: str | None = None
    children_ids: list[str] = None
    source_file: str | None = None
    extraction_method: str | None = None
    processing_chain: list[str] = None

    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.processing_chain is None:
            self.processing_chain = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "source_file": self.source_file,
            "extraction_method": self.extraction_method,
            "processing_chain": self.processing_chain,
        }


@dataclass
class CanonicalMetadata:
    """Metadata for canonical units."""
    content_type: str
    modality: str
    size_bytes: int
    token_count: int
    language: str | None = None
    encoding: str = "utf-8"
    tags: list[str] = None
    custom_attributes: dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_attributes is None:
            self.custom_attributes = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content_type": self.content_type,
            "modality": self.modality,
            "size_bytes": self.size_bytes,
            "token_count": self.token_count,
            "language": self.language,
            "encoding": self.encoding,
            "tags": self.tags,
            "custom_attributes": self.custom_attributes,
        }


@dataclass
class CanonicalRawUnit:
    """Immutable canonical raw unit with full provenance.

    Represents the base immutable record for all content in the system.
    Maintains canonical truth while enabling version tracking and lineage.
    """
    identifier: CanonicalIdentifier
    unit_type: CanonicalUnitType
    status: CanonicalUnitStatus
    content: str
    lineage: CanonicalLineage
    metadata: CanonicalMetadata

    def is_active(self) -> bool:
        """Check if unit is active."""
        return self.status == CanonicalUnitStatus.ACTIVE

    def is_tombstoned(self) -> bool:
        """Check if unit is tombstoned."""
        return self.status == CanonicalUnitStatus.TOMBSTONED

    def get_canonical_text(self) -> str:
        """Get the canonical text content (immutable)."""
        return self.content

    def get_size_estimate(self) -> int:
        """Get size estimate in bytes."""
        return len(self.content.encode(self.metadata.encoding))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "identifier": self.identifier.to_dict(),
            "unit_type": self.unit_type.value,
            "status": self.status.value,
            "content": self.content,
            "lineage": self.lineage.to_dict(),
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanonicalRawUnit":
        """Create from dictionary."""
        identifier_data = data["identifier"]
        identifier = CanonicalIdentifier(
            unit_id=identifier_data["unit_id"],
            version=identifier_data["version"],
            checksum=identifier_data["checksum"],
            created_at=datetime.fromisoformat(identifier_data["created_at"]),
        )

        lineage_data = data["lineage"]
        lineage = CanonicalLineage(
            parent_id=lineage_data.get("parent_id"),
            children_ids=lineage_data.get("children_ids", []),
            source_file=lineage_data.get("source_file"),
            extraction_method=lineage_data.get("extraction_method"),
            processing_chain=lineage_data.get("processing_chain", []),
        )

        metadata_data = data["metadata"]
        metadata = CanonicalMetadata(
            content_type=metadata_data["content_type"],
            modality=metadata_data["modality"],
            size_bytes=metadata_data["size_bytes"],
            token_count=metadata_data["token_count"],
            language=metadata_data.get("language"),
            encoding=metadata_data.get("encoding", "utf-8"),
            tags=metadata_data.get("tags", []),
            custom_attributes=metadata_data.get("custom_attributes", {}),
        )

        return cls(
            identifier=identifier,
            unit_type=CanonicalUnitType(data["unit_type"]),
            status=CanonicalUnitStatus(data["status"]),
            content=data["content"],
            lineage=lineage,
            metadata=metadata,
        )


@dataclass
class CanonicalDiff:
    """Difference between two canonical units."""
    old_unit: CanonicalRawUnit | None
    new_unit: CanonicalRawUnit
    change_type: str  # "created", "updated", "deleted", "tombstoned"
    changes: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "old_unit_id": self.old_unit.identifier.unit_id if self.old_unit else None,
            "new_unit_id": self.new_unit.identifier.unit_id,
            "change_type": self.change_type,
            "changes": self.changes,
            "timestamp": self.new_unit.identifier.created_at.isoformat(),
        }
