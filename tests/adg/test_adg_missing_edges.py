"""Test ADG missing edges functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.adg import adg_lifecycle
from agentic_core.adg.schema import EDGE_TYPES


@pytest.mark.unit
class TestAdgMissingEdges:
    """Test ADG missing edges functionality."""

    def test_missing_edges_detection_imports(self):
        """Test missing edges detection module imports."""
        assert adg_lifecycle is not None

    def test_adg_edge_builder_exists(self):
        """Test ADG edge builder module exists."""
        edge_builder = REPO_ROOT / "agentic_core" / "adg" / "extraction" / "edge_builder.py"
        assert edge_builder.exists()

    def test_adg_schema_has_edge_types(self):
        """Test ADG schema has edge types defined."""
        assert isinstance(EDGE_TYPES, (list, tuple, set, frozenset))
        assert len(EDGE_TYPES) > 0
