"""Test FileIoImplAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFileIoImplAdg:
    """Test FileIoImplAdg functionality."""

    def test_file_io_impl_adg_imports(self):
        """Test file_io_impl_adg module imports."""
        from agentic_core import file_io_impl_adg

        assert file_io_impl_adg is not None

    def test_file_io_impl_adg_class(self):
        """Test FileIoImplAdg class exists."""
        from agentic_core import FileIoImplAdg

        assert FileIoImplAdg is not None

    def test_file_io_impl_adg_callable(self):
        """Test file_io_impl_adg functions are callable."""
        from agentic_core import validate_file_io_impl_adg

        assert callable(validate_file_io_impl_adg)
