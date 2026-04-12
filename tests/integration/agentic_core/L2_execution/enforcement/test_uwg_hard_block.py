"""Test UwgHardBlock functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestUwgHardBlock:
    """Test UwgHardBlock functionality."""

    def test_uwg_hard_block_imports(self):
        """Test uwg_hard_block module imports."""
        from agentic_core import uwg_hard_block

        assert uwg_hard_block is not None

    def test_uwg_hard_block_class(self):
        """Test UwgHardBlock class exists."""
        from agentic_core import UwgHardBlock

        assert UwgHardBlock is not None

    def test_uwg_hard_block_callable(self):
        """Test uwg_hard_block functions are callable."""
        from agentic_core import validate_uwg_hard_block

        assert callable(validate_uwg_hard_block)
