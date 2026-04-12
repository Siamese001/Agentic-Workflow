"""Test SchemasAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSchemasAdg:
    """Test SchemasAdg functionality."""

    def test_schemas_adg_imports(self):
        """Test schemas_adg module imports."""
        from agentic_core import schemas_adg

        assert schemas_adg is not None

    def test_schemas_adg_class(self):
        """Test SchemasAdg class exists."""
        from agentic_core import SchemasAdg

        assert SchemasAdg is not None

    def test_schemas_adg_callable(self):
        """Test schemas_adg functions are callable."""
        from agentic_core import validate_schemas_adg

        assert callable(validate_schemas_adg)
