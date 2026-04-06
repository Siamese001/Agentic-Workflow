"""Raw Unit Factory.

Creates canonical raw units with immutable base records, unique identifiers,
and comprehensive provenance tracking for Pipeline B Phase B2.
"""

import hashlib
import logging
import uuid
from datetime import datetime

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

from .canonical_types import (
    CanonicalDiff,
    CanonicalIdentifier,
    CanonicalLineage,
    CanonicalMetadata,
    CanonicalRawUnit,
    CanonicalUnitStatus,
    CanonicalUnitType,
)

# Import ingestion components
try:
    from agentic_core.knowledge.ingestion.modality_types import ContentMetadata, ContentType, DocumentModality
except ImportError:
    # Fallback for testing
    ContentMetadata = None
    ContentType = None
    DocumentModality = None

log = logging.getLogger(__name__)


class RawUnitFactory:
    """Factory for creating canonical raw units with immutable base records.

    The RawUnitFactory implements Pipeline B Phase B2: CANONICAL RAW UNIT.
    It establishes the base immutable record with proper identifier generation,
    version tracking, and comprehensive provenance metadata.
    """

    def __init__(self):
        """Initialize the raw unit factory."""
        self._unit_counter: dict[str, int] = {}
        self._checksum_cache: dict[str, str] = {}

    def create_from_content(
        self,
        content: str,
        unit_type: CanonicalUnitType,
        source_file: str | None = None,
        parent_id: str | None = None,
        extraction_method: str | None = None,
        content_metadata: ContentMetadata | None = None,
        custom_tags: list[str] | None = None,
        custom_attributes: dict[str, str] | None = None,
    ) -> CanonicalRawUnit:
        """Create a canonical raw unit from content.

        Args:
            content: The content to create unit from
            unit_type: Type of unit being created
            source_file: Source file path
            parent_id: Parent unit ID for lineage
            extraction_method: Method used to extract content
            content_metadata: Content metadata from ingestion
            custom_tags: Additional tags for the unit
            custom_attributes: Additional custom attributes

        Returns:
            CanonicalRawUnit with full provenance
        """
        trace_id = f"create_unit_{uuid.uuid4().hex[:8]}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "RawUnitFactory.create_from_content"
        )

        # Generate unique identifier
        unit_id = self._generate_unit_id(content, unit_type)
        checksum = self._calculate_checksum(content)

        # Get or create version
        version = self._get_next_version(unit_id)

        # Create identifier
        identifier = CanonicalIdentifier(
            unit_id=unit_id,
            version=version,
            checksum=checksum,
            created_at=datetime.utcnow(),
        )

        # Create lineage
        lineage = CanonicalLineage(
            parent_id=parent_id,
            source_file=source_file,
            extraction_method=extraction_method,
            processing_chain=[extraction_method] if extraction_method else [],
        )

        # Create metadata
        metadata = self._create_metadata(content, unit_type, content_metadata, custom_tags, custom_attributes)

        # Create the canonical unit
        unit = CanonicalRawUnit(
            identifier=identifier,
            unit_type=unit_type,
            status=CanonicalUnitStatus.ACTIVE,
            content=content,
            lineage=lineage,
            metadata=metadata,
        )

        log.debug(f"Created canonical unit: {unit_id}:v{version}")
        return unit

    def create_from_ingestion_result(
        self,
        ingestion_metadata: ContentMetadata,
        content: str,
        unit_type: CanonicalUnitType = CanonicalUnitType.DOCUMENT,
    ) -> CanonicalRawUnit:
        """Create canonical unit from ingestion result.

        Args:
            ingestion_metadata: Metadata from ingestion process
            content: Extracted content
            unit_type: Type of unit to create

        Returns:
            CanonicalRawUnit with ingestion-based provenance
        """
        return self.create_from_content(
            content=content,
            unit_type=unit_type,
            source_file=ingestion_metadata.file_path,
            extraction_method="intake_clerk",
            content_metadata=ingestion_metadata,
            custom_tags=[ingestion_metadata.modality.value, ingestion_metadata.content_type.value],
        )

    def create_child_units(
        self,
        parent_unit: CanonicalRawUnit,
        child_contents: list[str],
        child_type: CanonicalUnitType,
        extraction_method: str | None = None,
    ) -> list[CanonicalRawUnit]:
        """Create child units from a parent unit.

        Args:
            parent_unit: Parent canonical unit
            child_contents: List of child content strings
            child_type: Type of child units to create
            extraction_method: Method used for child extraction

        Returns:
            List of child canonical units
        """
        trace_id = f"create_children_{parent_unit.identifier.unit_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "RawUnitFactory.create_child_units"
        )

        child_units = []

        for i, content in enumerate(child_contents):
            child_unit = self.create_from_content(
                content=content,
                unit_type=child_type,
                source_file=parent_unit.lineage.source_file,
                parent_id=parent_unit.identifier.unit_id,
                extraction_method=extraction_method or f"child_extraction_{child_type.value}",
                custom_tags=[f"child_{i}", f"parent_{parent_unit.identifier.unit_id}"],
            )
            child_units.append(child_unit)

        # Update parent lineage with children
        parent_unit.lineage.children_ids = [unit.identifier.unit_id for unit in child_units]

        log.info(f"Created {len(child_units)} child units for parent {parent_unit.identifier.unit_id}")
        return child_units

    def create_versioned_unit(
        self,
        existing_unit: CanonicalRawUnit,
        new_content: str,
        change_reason: str | None = None,
    ) -> tuple[CanonicalRawUnit, CanonicalDiff]:
        """Create a new version of an existing unit.

        Args:
            existing_unit: Existing canonical unit
            new_content: New content for the unit
            change_reason: Reason for the change

        Returns:
            Tuple of (new_unit, diff) showing the changes
        """
        trace_id = f"version_{existing_unit.identifier.unit_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "RawUnitFactory.create_versioned_unit"
        )

        # Check if content actually changed
        new_checksum = self._calculate_checksum(new_content)
        if new_checksum == existing_unit.identifier.checksum:
            log.debug(f"No content change detected for {existing_unit.identifier.unit_id}")
            return existing_unit, CanonicalDiff(
                old_unit=None,
                new_unit=existing_unit,
                change_type="unchanged",
                changes=[],
            )

        # Create new version
        new_unit = self.create_from_content(
            content=new_content,
            unit_type=existing_unit.unit_type,
            source_file=existing_unit.lineage.source_file,
            parent_id=existing_unit.lineage.parent_id,
            extraction_method=existing_unit.lineage.extraction_method,
        )

        # Copy lineage and processing chain
        new_unit.lineage = CanonicalLineage(
            parent_id=existing_unit.lineage.parent_id,
            children_ids=existing_unit.lineage.children_ids,
            source_file=existing_unit.lineage.source_file,
            extraction_method=existing_unit.lineage.extraction_method,
            processing_chain=existing_unit.lineage.processing_chain + ["version_update"],
        )

        # Copy metadata with updates
        new_unit.metadata = self._create_metadata(
            new_content,
            existing_unit.unit_type,
            None,  # No content metadata for version updates
            existing_unit.metadata.tags,
            existing_unit.metadata.custom_attributes,
        )

        # Ensure we have the correct version number
        new_unit.identifier.version = existing_unit.identifier.version + 1

        # Mark old unit as superseded
        existing_unit.status = CanonicalUnitStatus.SUPERSEDED

        # Create diff
        changes = [f"Content updated: {change_reason or 'No reason provided'}"]
        if len(new_content) != len(existing_unit.content):
            changes.append(f"Size changed: {len(existing_unit.content)} -> {len(new_content)} characters")

        diff = CanonicalDiff(
            old_unit=existing_unit,
            new_unit=new_unit,
            change_type="updated",
            changes=changes,
        )

        log.info(f"Created version {new_unit.identifier.version} for unit {new_unit.identifier.unit_id}")
        return new_unit, diff

    def tombstone_unit(self, unit: CanonicalRawUnit, reason: str | None = None) -> CanonicalRawUnit:
        """Create a tombstoned version of a unit.

        Args:
            unit: Unit to tombstone
            reason: Reason for tombstoning

        Returns:
            Tombstoned unit
        """
        trace_id = f"tombstone_{unit.identifier.unit_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L2_EXECUTION, "RawUnitFactory.tombstone_unit"
        )

        # Create tombstoned version
        tombstoned_unit = CanonicalRawUnit(
            identifier=CanonicalIdentifier(
                unit_id=unit.identifier.unit_id,
                version=self._get_next_version(unit.identifier.unit_id),
                checksum=self._calculate_checksum(""),
                created_at=datetime.utcnow(),
            ),
            unit_type=unit.unit_type,
            status=CanonicalUnitStatus.TOMBSTONED,
            content="",  # Empty content for tombstoned units
            lineage=CanonicalLineage(
                parent_id=unit.lineage.parent_id,
                children_ids=unit.lineage.children_ids,
                source_file=unit.lineage.source_file,
                extraction_method="tombstone",
                processing_chain=unit.lineage.processing_chain + ["tombstone"],
            ),
            metadata=CanonicalMetadata(
                content_type=unit.metadata.content_type,
                modality=unit.metadata.modality,
                size_bytes=0,
                token_count=0,
                language=unit.metadata.language,
                encoding=unit.metadata.encoding,
                tags=unit.metadata.tags + ["tombstoned"],
                custom_attributes={
                    **unit.metadata.custom_attributes,
                    "tombstone_reason": reason or "Unknown",
                    "original_checksum": unit.identifier.checksum,
                },
            ),
        )

        # Mark original unit as superseded
        unit.status = CanonicalUnitStatus.SUPERSEDED

        log.info(f"Tombstoned unit {unit.identifier.unit_id}: {reason}")
        return tombstoned_unit

    def _generate_unit_id(self, content: str, unit_type: CanonicalUnitType) -> str:
        """Generate unique unit ID based on content and type."""
        # Create content hash for uniqueness
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        type_prefix = unit_type.value[:3].upper()
        return f"{type_prefix}_{content_hash}"

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_next_version(self, unit_id: str) -> int:
        """Get next version number for a unit ID."""
        current = self._unit_counter.get(unit_id, 0)
        next_version = current + 1
        self._unit_counter[unit_id] = next_version
        return next_version

    def _create_metadata(
        self,
        content: str,
        unit_type: CanonicalUnitType,
        content_metadata: ContentMetadata | None,
        custom_tags: list[str] | None,
        custom_attributes: dict[str, str] | None,
    ) -> CanonicalMetadata:
        """Create metadata for a canonical unit."""
        # Base metadata from content analysis
        size_bytes = len(content.encode('utf-8'))
        token_count = len(content) // 4  # Rough approximation

        # Default values
        content_type = "text/plain"
        modality = "text_only"
        language = "en"

        # Override with ingestion metadata if available
        if content_metadata:
            content_type = content_metadata.content_type.value
            modality = content_metadata.modality.value
            language = content_metadata.language or "en"
            token_count = content_metadata.estimated_tokens

        # Merge tags
        tags = [unit_type.value]
        if custom_tags:
            tags.extend(custom_tags)
        if content_metadata:
            tags.extend([content_metadata.modality.value, content_metadata.content_type.value])

        # Merge custom attributes
        attributes = {}
        if custom_attributes:
            attributes.update(custom_attributes)
        if content_metadata:
            attributes.update({
                "file_size": content_metadata.file_size_bytes,
                "has_tables": content_metadata.has_tables,
                "has_images": content_metadata.has_images,
                "has_code_blocks": content_metadata.has_code_blocks,
                "has_headings": content_metadata.has_headings,
            })

        return CanonicalMetadata(
            content_type=content_type,
            modality=modality,
            size_bytes=size_bytes,
            token_count=token_count,
            language=language,
            tags=tags,
            custom_attributes=attributes,
        )


# Global factory instance
_global_factory: RawUnitFactory | None = None


def get_raw_unit_factory() -> RawUnitFactory:
    """Get or create the global raw unit factory."""
    global _global_factory
    if _global_factory is None:
        _global_factory = RawUnitFactory()
    return _global_factory


def create_canonical_unit(
    content: str,
    unit_type: CanonicalUnitType,
    source_file: str | None = None,
    **kwargs,
) -> CanonicalRawUnit:
    """Convenience function to create a canonical unit."""
    return get_raw_unit_factory().create_from_content(content, unit_type, source_file, **kwargs)
