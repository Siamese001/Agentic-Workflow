"""Test AllprovidersdownerrorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAllprovidersdownerrorAdg:
    """Test AllprovidersdownerrorAdg functionality."""

    def test_AllProvidersDownError_adg_imports(self):
        """Test AllProvidersDownError_adg module imports."""
        from agentic_core import AllProvidersDownError_adg
        assert AllProvidersDownError_adg is not None

    def test_AllProvidersDownError_adg_class(self):
        """Test AllprovidersdownerrorAdg class exists."""
        from agentic_core import AllprovidersdownerrorAdg
        assert AllprovidersdownerrorAdg is not None

    def test_AllProvidersDownError_adg_callable(self):
        """Test AllProvidersDownError_adg functions are callable."""
        from agentic_core import validate_AllProvidersDownError_adg
        assert callable(validate_AllProvidersDownError_adg)
