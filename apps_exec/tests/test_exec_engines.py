"""Tests for apps_exec engine components."""


from apps_exec.engines.brief_assembly_engine import (
    BriefAssemblyEngine,
)
from apps_exec.engines.ingestion_engine import (
    IngestionEngine,
)


class TestBriefAssemblyEngine:
    """Test BriefAssemblyEngine."""

    def test_engine_import(self):
        """Test that BriefAssemblyEngine can be imported."""
        assert BriefAssemblyEngine is not None

    def test_engine_class_exists(self):
        """Test that BriefAssemblyEngine class exists."""
        assert callable(BriefAssemblyEngine)


class TestIngestionEngine:
    """Test IngestionEngine."""

    def test_engine_import(self):
        """Test that IngestionEngine can be imported."""
        assert IngestionEngine is not None

    def test_engine_class_exists(self):
        """Test that IngestionEngine class exists."""
        assert callable(IngestionEngine)
