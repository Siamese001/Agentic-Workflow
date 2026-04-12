"""Test Protocol functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProtocol:
    """Test Protocol functionality."""

    def test_protocol_imports(self):
        """Test protocol module imports."""
        from agentic_core import protocol

        assert protocol is not None

    def test_protocol_class(self):
        """Test Protocol class exists."""
        from agentic_core import Protocol

        assert Protocol is not None

    def test_protocol_callable(self):
        """Test protocol functions are callable."""
        from agentic_core import validate_protocol

        assert callable(validate_protocol)
