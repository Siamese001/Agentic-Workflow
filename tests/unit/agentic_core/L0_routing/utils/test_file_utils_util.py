"""Test FileUtilsUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFileUtilsUtil:
    """Test FileUtilsUtil functionality."""

    def test_file_utils_util_imports(self):
        """Test file_utils_util module imports."""
        from agentic_core import file_utils_util

        assert file_utils_util is not None

    def test_file_utils_util_class(self):
        """Test FileUtilsUtil class exists."""
        from agentic_core import FileUtilsUtil

        assert FileUtilsUtil is not None

    def test_file_utils_util_callable(self):
        """Test file_utils_util functions are callable."""
        from agentic_core import validate_file_utils_util

        assert callable(validate_file_utils_util)
