"""Test ValidationToolsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidationToolsAdg:
    """Test ValidationToolsAdg functionality."""

    def test_validation_tools_adg_imports(self):
        """Test validation_tools_adg module imports."""
        from agentic_core import validation_tools_adg

        assert validation_tools_adg is not None

    def test_validation_tools_adg_class(self):
        """Test ValidationToolsAdg class exists."""
        from agentic_core import ValidationToolsAdg

        assert ValidationToolsAdg is not None

    def test_validation_tools_adg_callable(self):
        """Test validation_tools_adg functions are callable."""
        from agentic_core import validate_validation_tools_adg

        assert callable(validate_validation_tools_adg)
