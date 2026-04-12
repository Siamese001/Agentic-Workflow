"""Test ParentChildAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestParentChildAdg:
    """Test ParentChildAdg functionality."""

    def test_parent_child_adg_imports(self):
        """Test parent_child_adg module imports."""
        from agentic_core import parent_child_adg

        assert parent_child_adg is not None

    def test_parent_child_adg_class(self):
        """Test ParentChildAdg class exists."""
        from agentic_core import ParentChildAdg

        assert ParentChildAdg is not None

    def test_parent_child_adg_callable(self):
        """Test parent_child_adg functions are callable."""
        from agentic_core import validate_parent_child_adg

        assert callable(validate_parent_child_adg)
