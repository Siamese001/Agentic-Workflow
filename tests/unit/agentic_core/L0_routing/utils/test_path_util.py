"""Test PathUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPathUtil:
    """Test PathUtil functionality."""

    def test_path_util_imports(self):
        """Test path_util module imports."""
        from agentic_core import path_util
        assert path_util is not None

    def test_path_util_class(self):
        """Test PathUtil class exists."""
        from agentic_core import PathUtil
        assert PathUtil is not None

    def test_path_util_callable(self):
        """Test path_util functions are callable."""
        from agentic_core import validate_path_util
        assert callable(validate_path_util)
