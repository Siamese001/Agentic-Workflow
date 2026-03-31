"""Test SsotUtf8Output functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotUtf8Output:
    """Test SsotUtf8Output functionality."""

    def test_ssot_utf8_output_imports(self):
        """Test ssot_utf8_output module imports."""
        from agentic_core import ssot_utf8_output
        assert ssot_utf8_output is not None

    def test_ssot_utf8_output_class(self):
        """Test SsotUtf8Output class exists."""
        from agentic_core import SsotUtf8Output
        assert SsotUtf8Output is not None

    def test_ssot_utf8_output_callable(self):
        """Test ssot_utf8_output functions are callable."""
        from agentic_core import validate_ssot_utf8_output
        assert callable(validate_ssot_utf8_output)
