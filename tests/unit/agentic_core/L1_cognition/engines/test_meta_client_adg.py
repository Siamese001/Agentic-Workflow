"""Test MetaClientAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaClientAdg:
    """Test MetaClientAdg functionality."""

    def test_meta_client_adg_imports(self):
        """Test meta_client_adg module imports."""
        from agentic_core import meta_client_adg
        assert meta_client_adg is not None

    def test_meta_client_adg_class(self):
        """Test MetaClientAdg class exists."""
        from agentic_core import MetaClientAdg
        assert MetaClientAdg is not None

    def test_meta_client_adg_callable(self):
        """Test meta_client_adg functions are callable."""
        from agentic_core import validate_meta_client_adg
        assert callable(validate_meta_client_adg)
