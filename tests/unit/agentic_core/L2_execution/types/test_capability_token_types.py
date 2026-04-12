"""Test CapabilityTokenTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCapabilityTokenTypes:
    """Test CapabilityTokenTypes functionality."""

    def test_capability_token_types_imports(self):
        """Test capability_token_types module imports."""
        from agentic_core import capability_token_types

        assert capability_token_types is not None

    def test_capability_token_types_class(self):
        """Test CapabilityTokenTypes class exists."""
        from agentic_core import CapabilityTokenTypes

        assert CapabilityTokenTypes is not None

    def test_capability_token_types_callable(self):
        """Test capability_token_types functions are callable."""
        from agentic_core import validate_capability_token_types

        assert callable(validate_capability_token_types)
