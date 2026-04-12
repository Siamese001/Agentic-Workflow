"""Test ProtocolAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProtocolAdg:
    """Test ProtocolAdg functionality."""

    def test_protocol_adg_imports(self):
        """Test protocol_adg module imports."""
        from agentic_core import protocol_adg

        assert protocol_adg is not None

    def test_protocol_adg_class(self):
        """Test ProtocolAdg class exists."""
        from agentic_core import ProtocolAdg

        assert ProtocolAdg is not None

    def test_protocol_adg_callable(self):
        """Test protocol_adg functions are callable."""
        from agentic_core import validate_protocol_adg

        assert callable(validate_protocol_adg)
