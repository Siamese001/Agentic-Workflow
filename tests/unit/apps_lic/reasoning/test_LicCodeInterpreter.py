"""Test Liccodeinterpreter functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLiccodeinterpreter:
    """Test Liccodeinterpreter functionality."""

    def test_LicCodeInterpreter_imports(self):
        """Test LicCodeInterpreter module imports."""
        from agentic_core import LicCodeInterpreter

        assert LicCodeInterpreter is not None

    def test_LicCodeInterpreter_class(self):
        """Test Liccodeinterpreter class exists."""
        from agentic_core import Liccodeinterpreter

        assert Liccodeinterpreter is not None

    def test_LicCodeInterpreter_callable(self):
        """Test LicCodeInterpreter functions are callable."""
        from agentic_core import validate_LicCodeInterpreter

        assert callable(validate_LicCodeInterpreter)
