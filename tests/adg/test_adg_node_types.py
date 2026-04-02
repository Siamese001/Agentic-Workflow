"""Test ADG node types functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.schema import NodeType
from agentic_core.adg.schema import NODE_TYPES


@pytest.mark.unit
class TestAdgNodeTypes:
    """Test ADG node types functionality."""

    def test_node_types_imports(self):
        """Test node types module imports."""
        assert NodeType is not None

    def test_adg_schema_has_node_types(self):
        """Test ADG schema has node types defined."""
        assert isinstance(NODE_TYPES, (list, tuple, set, frozenset))
        assert len(NODE_TYPES) > 0

    def test_node_type_has_required_types(self):
        """Test node type has required types."""
        required = ["module", "class", "function", "method"]
        for rt in required:
            assert any(rt in str(nt).lower() for nt in NODE_TYPES)
