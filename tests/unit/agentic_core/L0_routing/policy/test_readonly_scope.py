"""Test ReadonlyScope functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReadonlyScope:
    """Test ReadonlyScope functionality."""

    def test_readonly_scope_imports(self):
        """Test readonly_scope module imports."""
        from agentic_core import readonly_scope

        assert readonly_scope is not None

    def test_readonly_scope_class(self):
        """Test ReadonlyScope class exists."""
        from agentic_core import ReadonlyScope

        assert ReadonlyScope is not None

    def test_readonly_scope_callable(self):
        """Test readonly_scope functions are callable."""
        from agentic_core import validate_readonly_scope

        assert callable(validate_readonly_scope)
