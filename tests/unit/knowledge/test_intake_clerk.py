"""Test Intake Clerk and Canonical Unit System.

Tests for Pipeline B Phase B1 and B2: Intake & Modality Detection
and Canonical Raw Unit establishment.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.knowledge.canonical.canonical_store import CanonicalStore
from agentic_core.knowledge.canonical.canonical_types import CanonicalUnitStatus, CanonicalUnitType
from agentic_core.knowledge.canonical.raw_unit_factory import RawUnitFactory
from agentic_core.knowledge.ingestion.intake_clerk import IntakeClerk
from agentic_core.knowledge.ingestion.modality_types import ContentType, DocumentModality


class TestIntakeClerk:
    """Test the Intake Clerk functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.intake_clerk = IntakeClerk()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_modality_text_only(self):
        """Test modality detection for text-only content."""
        content = "This is a simple text document with plain content."

        # Create temporary file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text(content)

        modality = self.intake_clerk.detect_modality(test_file, content)
        assert modality == DocumentModality.TEXT_ONLY

    def test_detect_modality_visual_heavy(self):
        """Test modality detection for visual-heavy content."""
        content = """
        # Document with Visual Content

        ![Chart](chart.png)

        | Column 1 | Column 2 |
        |----------|----------|
        | Data 1   | Data 2   |

        ![Diagram](diagram.svg)
        """

        test_file = self.temp_dir / "visual.md"
        test_file.write_text(content)

        modality = self.intake_clerk.detect_modality(test_file, content)
        assert modality in [DocumentModality.VISUAL_HEAVY, DocumentModality.MIXED_MODAL]

    def test_detect_modality_code_base(self):
        """Test modality detection for code content."""
        content = """
        ```python
        def hello_world():
            print("Hello, World!")
            return True

        if __name__ == "__main__":
            hello_world()
        ```
        """

        test_file = self.temp_dir / "code.py"
        test_file.write_text(content)

        modality = self.intake_clerk.detect_modality(test_file, content)
        assert modality == DocumentModality.CODE_BASE

    def test_extract_metadata(self):
        """Test metadata extraction."""
        content = """
# Sample Document

This is a sample document with a heading and some content.

## Section 2

More content here.
        """

        test_file = self.temp_dir / "sample.md"
        test_file.write_text(content)

        metadata = self.intake_clerk.extract_metadata(test_file, content)

        assert metadata.file_path == str(test_file)
        assert metadata.content_type == ContentType.MARKDOWN
        assert metadata.has_headings == True
        assert metadata.estimated_tokens > 0
        assert metadata.checksum is not None
        # Should detect as structured text due to headings
        assert metadata.modality in [DocumentModality.STRUCTURED_TEXT, DocumentModality.CODE_BASE]

    def test_ingest_document_success(self):
        """Test successful document ingestion."""
        content = "Test document content for ingestion."

        test_file = self.temp_dir / "test.txt"
        test_file.write_text(content)

        result = self.intake_clerk.ingest_document(test_file)

        assert result.success == True
        assert result.content == content
        assert result.metadata is not None
        assert result.processing_time_ms is not None
        assert result.error_message is None

    def test_ingest_document_not_found(self):
        """Test ingestion of non-existent file."""
        test_file = self.temp_dir / "nonexistent.txt"

        result = self.intake_clerk.ingest_document(test_file)

        assert result.success == False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()

    def test_ingest_batch(self):
        """Test batch ingestion."""
        # Create multiple test files
        files = []
        for i in range(3):
            content = f"Test content for file {i}"
            test_file = self.temp_dir / f"test_{i}.txt"
            test_file.write_text(content)
            files.append(test_file)

        results = self.intake_clerk.ingest_batch(files)

        assert len(results) == 3
        assert all(result.success for result in results)

        stats = self.intake_clerk.get_ingestion_stats(results)
        assert stats["total_documents"] == 3
        assert stats["successful"] == 3
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0


class TestRawUnitFactory:
    """Test the Raw Unit Factory functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RawUnitFactory()

    def test_create_canonical_unit(self):
        """Test creating a canonical unit from content."""
        content = "This is test content for a canonical unit."

        unit = self.factory.create_from_content(
            content=content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
            extraction_method="test_extraction",
        )

        assert unit.content == content
        assert unit.unit_type == CanonicalUnitType.DOCUMENT
        assert unit.status.value == "active"
        assert unit.identifier.unit_id is not None
        assert unit.identifier.version == 1
        assert unit.identifier.checksum is not None
        assert unit.lineage.source_file == "test.txt"
        assert unit.lineage.extraction_method == "test_extraction"
        assert unit.metadata.size_bytes > 0
        assert unit.metadata.token_count > 0

    def test_create_child_units(self):
        """Test creating child units from a parent."""
        parent_content = "Parent document content."
        child_contents = ["Child 1 content.", "Child 2 content."]

        parent_unit = self.factory.create_from_content(
            content=parent_content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="parent.txt",
        )

        child_units = self.factory.create_child_units(
            parent_unit=parent_unit,
            child_contents=child_contents,
            child_type=CanonicalUnitType.CHUNK,
            extraction_method="test_chunking",
        )

        assert len(child_units) == 2
        assert all(unit.unit_type == CanonicalUnitType.CHUNK for unit in child_units)
        assert all(unit.lineage.parent_id == parent_unit.identifier.unit_id for unit in child_units)
        assert len(parent_unit.lineage.children_ids) == 2

    def test_create_versioned_unit(self):
        """Test creating a new version of an existing unit."""
        original_content = "Original content."
        updated_content = "Updated content with more text."

        original_unit = self.factory.create_from_content(
            content=original_content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )

        new_unit, diff = self.factory.create_versioned_unit(
            existing_unit=original_unit,
            new_content=updated_content,
            change_reason="Content update test",
        )

        assert new_unit.content == updated_content
        assert new_unit.identifier.version == 2
        assert original_unit.status.value == "superseded"
        assert diff.change_type == "updated"
        assert len(diff.changes) > 0

    def test_create_versioned_unit_no_change(self):
        """Test versioning when content doesn't change."""
        content = "Test content that won't change."

        original_unit = self.factory.create_from_content(
            content=content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )

        new_unit, diff = self.factory.create_versioned_unit(
            existing_unit=original_unit,
            new_content=content,  # Same content
        )

        assert new_unit == original_unit  # Should return the same unit
        assert diff.change_type == "unchanged"
        assert len(diff.changes) == 0

    def test_tombstone_unit(self):
        """Test tombstoning a unit."""
        content = "Content to be tombstoned."

        unit = self.factory.create_from_content(
            content=content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )

        tombstoned_unit = self.factory.tombstone_unit(unit, reason="Test tombstoning")

        assert tombstoned_unit.status.value == "tombstoned"
        assert tombstoned_unit.content == ""
        assert tombstoned_unit.metadata.size_bytes == 0
        assert unit.status.value == "superseded"
        assert "tombstoned" in tombstoned_unit.metadata.tags


class TestCanonicalStore:
    """Test the Canonical Store functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.store = CanonicalStore(self.temp_dir)
        self.factory = RawUnitFactory()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_and_retrieve_unit(self):
        """Test storing and retrieving a canonical unit."""
        content = "Test content for storage."

        unit = self.factory.create_from_content(
            content=content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )

        # Store the unit
        success = self.store.store_unit(unit)
        assert success == True

        # Retrieve the unit
        retrieved_unit = self.store.get_unit(unit.identifier.unit_id)

        assert retrieved_unit is not None
        assert retrieved_unit.content == content
        assert retrieved_unit.identifier.unit_id == unit.identifier.unit_id
        assert retrieved_unit.identifier.version == unit.identifier.version

    def test_get_latest_unit(self):
        """Test retrieving the latest version of a unit."""
        content1 = "Version 1 content."
        content2 = "Version 2 content."

        # Create and store first version
        unit1 = self.factory.create_from_content(
            content=content1,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )
        self.store.store_unit(unit1)

        # Create and store second version (note: different content = different unit_id)
        unit2, _ = self.factory.create_versioned_unit(unit1, content2, "Update test")
        self.store.store_unit(unit2)

        # Retrieve latest from the original unit's lineage
        # Since versioned units get new unit_ids, we need to check the original is superseded
        latest_unit = self.store.get_latest_unit(unit2.identifier.unit_id)  # Use the new unit_id

        assert latest_unit is not None
        assert latest_unit.content == content2
        assert latest_unit.identifier.version == 2

        # Check original unit is superseded
        original_retrieved = self.store.get_latest_unit(unit1.identifier.unit_id)
        assert original_retrieved.status == CanonicalUnitStatus.SUPERSEDED

    def test_find_by_checksum(self):
        """Test finding units by checksum."""
        content = "Content with specific checksum."

        unit = self.factory.create_from_content(
            content=content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="test.txt",
        )
        self.store.store_unit(unit)

        matches = self.store.find_by_checksum(unit.identifier.checksum)

        assert len(matches) == 1
        assert matches[0].identifier.unit_id == unit.identifier.unit_id

    def test_get_children(self):
        """Test retrieving child units."""
        parent_content = "Parent content."
        child_contents = ["Child 1", "Child 2"]

        parent_unit = self.factory.create_from_content(
            content=parent_content,
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="parent.txt",
        )

        child_units = self.factory.create_child_units(
            parent_unit=parent_unit,
            child_contents=child_contents,
            child_type=CanonicalUnitType.CHUNK,
        )

        # Store all units
        self.store.store_unit(parent_unit)
        for child_unit in child_units:
            self.store.store_unit(child_unit)

        # Retrieve children
        retrieved_children = self.store.get_children(parent_unit.identifier.unit_id)

        assert len(retrieved_children) == 2
        assert all(child.unit_type == CanonicalUnitType.CHUNK for child in retrieved_children)

    def test_get_active_units(self):
        """Test retrieving only active units."""
        # Create active unit
        active_unit = self.factory.create_from_content(
            content="Active content.",
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="active.txt",
        )

        # Create tombstoned unit
        tombstoned_unit = self.factory.create_from_content(
            content="To be tombstoned.",
            unit_type=CanonicalUnitType.DOCUMENT,
            source_file="tombstone.txt",
        )
        tombstoned_unit = self.factory.tombstone_unit(tombstoned_unit)

        # Store units
        self.store.store_unit(active_unit)
        self.store.store_unit(tombstoned_unit)

        # Get active units
        active_units = self.store.find_active_units()

        assert len(active_units) == 1
        assert active_units[0].identifier.unit_id == active_unit.identifier.unit_id
        assert active_units[0].is_active()

    def test_storage_stats(self):
        """Test storage statistics."""
        # Create and store multiple units
        for i in range(3):
            content = f"Test content {i}"
            unit = self.factory.create_from_content(
                content=content,
                unit_type=CanonicalUnitType.DOCUMENT,
                source_file=f"test_{i}.txt",
            )
            self.store.store_unit(unit)

        stats = self.store.get_storage_stats()

        assert stats["total_units"] == 3
        assert stats["active_units"] == 3
        assert stats["total_versions"] == 3
        assert stats["storage_size_bytes"] > 0
        assert stats["avg_versions_per_unit"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
