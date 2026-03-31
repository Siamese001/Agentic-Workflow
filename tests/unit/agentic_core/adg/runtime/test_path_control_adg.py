"""Test PathControlAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPathControlAdg:
    """Test PathControlAdg functionality."""

    def test_path_control_adg_imports(self):
        """Test path_control_adg module imports."""
        from agentic_core import path_control_adg
        assert path_control_adg is not None

    def test_path_control_adg_class(self):
        """Test PathControlAdg class exists."""
        from agentic_core import PathControlAdg
        assert PathControlAdg is not None

    def test_path_control_adg_callable(self):
        """Test path_control_adg functions are callable."""
        from agentic_core import validate_path_control_adg
        assert callable(validate_path_control_adg)
