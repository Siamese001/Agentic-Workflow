"""Test PoliciesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPoliciesAdg:
    """Test PoliciesAdg functionality."""

    def test_policies_adg_imports(self):
        """Test policies_adg module imports."""
        from agentic_core import policies_adg

        assert policies_adg is not None

    def test_policies_adg_class(self):
        """Test PoliciesAdg class exists."""
        from agentic_core import PoliciesAdg

        assert PoliciesAdg is not None

    def test_policies_adg_callable(self):
        """Test policies_adg functions are callable."""
        from agentic_core import validate_policies_adg

        assert callable(validate_policies_adg)
