"""ADG Static Scanner Tests — Structural Validation.

Tests for static_scanner.py structure, imports, and data classes.
"""
import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


@pytest.mark.unit
class TestStaticScannerImports:
    """Test that static_scanner components can be imported."""

    def test_import_edge_dataclass(self):
        """Test Edge dataclass can be imported."""
        from agentic_core.adg.extraction.static_scanner import Edge
        assert Edge is not None

    def test_import_scan_manifest(self):
        """Test ScanManifest can be imported."""
        from agentic_core.adg.extraction.static_scanner import ScanManifest
        assert ScanManifest is not None

    def test_import_import_visitor(self):
        """Test _ImportVisitor can be imported."""
        from agentic_core.adg.extraction.static_scanner import _ImportVisitor
        assert _ImportVisitor is not None

    def test_import_call_visitor(self):
        """Test _CallVisitor can be imported."""
        from agentic_core.adg.extraction.static_scanner import _CallVisitor
        assert _CallVisitor is not None


@pytest.mark.unit
class TestEdgeDataclass:
    """Tests for Edge data structure."""

    def test_edge_creation(self):
        """Test Edge can be created with required fields."""
        from agentic_core.adg.extraction.static_scanner import Edge
        edge = Edge(
            from_name="test_from",
            relation_type="test_relation",
            to_name="test_to",
            edge_kind="test_kind",
            source_file="test.py",
            line_no=1,
            symbol="test_symbol"
        )
        assert edge.from_name == "test_from"
        assert edge.relation_type == "test_relation"
        assert edge.to_name == "test_to"
        assert edge.edge_kind == "test_kind"

    def test_edge_defaults(self):
        """Test Edge field defaults work."""
        from agentic_core.adg.extraction.static_scanner import Edge
        edge = Edge(
            from_name="a",
            relation_type="calls",
            to_name="b",
            edge_kind="governance",
            source_file="file.py",
            line_no=1,
            symbol="call"
        )
        assert edge.confidence == 1.0  # default
        assert edge.semantic_type in ("", None)  # default


@pytest.mark.unit
class TestScanManifestDataclass:
    """Tests for ScanManifest functionality."""

    def test_scan_manifest_creation(self):
        """Test creation of scan manifest."""
        from agentic_core.adg.extraction.static_scanner import ScanManifest
        manifest = ScanManifest(
            discovered_module_count=10,
            parsed_module_count=8,
            edge_counts_by_graph={"imports": 15}
        )
        assert manifest.discovered_module_count == 10
        assert manifest.parsed_module_count == 8
        assert manifest.edge_counts_by_graph["imports"] == 15

    def test_scan_manifest_to_dict(self):
        """Test manifest serialization."""
        from agentic_core.adg.extraction.static_scanner import ScanManifest
        manifest = ScanManifest(
            discovered_module_count=10,
            parsed_module_count=8,
            edge_counts_by_graph={"imports": 15}
        )
        data = manifest.to_dict()
        assert isinstance(data, dict)
        assert 'discovered_module_count' in data
        assert 'parsed_module_count' in data
        assert data['discovered_module_count'] == 10
