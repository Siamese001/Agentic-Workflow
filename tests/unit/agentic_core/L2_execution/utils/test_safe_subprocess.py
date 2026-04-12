"""Test SafeSubprocess functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafeSubprocess:
    """Test SafeSubprocess functionality."""

    def test_safe_subprocess_imports(self):
        """Test safe_subprocess module imports."""
        from agentic_core import safe_subprocess

        assert safe_subprocess is not None

    def test_safe_subprocess_class(self):
        """Test SafeSubprocess class exists."""
        from agentic_core import SafeSubprocess

        assert SafeSubprocess is not None

    def test_safe_subprocess_callable(self):
        """Test safe_subprocess functions are callable."""
        from agentic_core import validate_safe_subprocess

        assert callable(validate_safe_subprocess)
