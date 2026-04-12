"""Test SsotAdapters functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotAdapters:
    """Test SsotAdapters functionality."""

    def test_ssot_adapters_imports(self):
        """Test ssot_adapters module imports."""
        from agentic_core import ssot_adapters

        assert ssot_adapters is not None

    def test_ssot_adapters_class(self):
        """Test SsotAdapters class exists."""
        from agentic_core import SsotAdapters

        assert SsotAdapters is not None

    def test_ssot_adapters_callable(self):
        """Test ssot_adapters functions are callable."""
        from agentic_core import validate_ssot_adapters

        assert callable(validate_ssot_adapters)
