"""Test WebSearchClientAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestWebSearchClientAdg:
    """Test WebSearchClientAdg functionality."""

    def test_web_search_client_adg_imports(self):
        """Test web_search_client_adg module imports."""
        from agentic_core import web_search_client_adg
        assert web_search_client_adg is not None

    def test_web_search_client_adg_class(self):
        """Test WebSearchClientAdg class exists."""
        from agentic_core import WebSearchClientAdg
        assert WebSearchClientAdg is not None

    def test_web_search_client_adg_callable(self):
        """Test web_search_client_adg functions are callable."""
        from agentic_core import validate_web_search_client_adg
        assert callable(validate_web_search_client_adg)
