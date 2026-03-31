"""Test IoInterceptionAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIoInterceptionAdg:
    """Test IoInterceptionAdg functionality."""

    def test_io_interception_adg_imports(self):
        """Test io_interception_adg module imports."""
        from agentic_core import io_interception_adg
        assert io_interception_adg is not None

    def test_io_interception_adg_class(self):
        """Test IoInterceptionAdg class exists."""
        from agentic_core import IoInterceptionAdg
        assert IoInterceptionAdg is not None

    def test_io_interception_adg_callable(self):
        """Test io_interception_adg functions are callable."""
        from agentic_core import validate_io_interception_adg
        assert callable(validate_io_interception_adg)
