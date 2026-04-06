"""Test Ivalidatorprotocol functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIvalidatorprotocol:
    """Test Ivalidatorprotocol functionality."""

    def test_IValidatorProtocol_imports(self):
        """Test IValidatorProtocol module imports."""
        from agentic_core import IValidatorProtocol
        assert IValidatorProtocol is not None

    def test_IValidatorProtocol_class(self):
        """Test Ivalidatorprotocol class exists."""
        from agentic_core import Ivalidatorprotocol
        assert Ivalidatorprotocol is not None

    def test_IValidatorProtocol_callable(self):
        """Test IValidatorProtocol functions are callable."""
        from agentic_core import validate_IValidatorProtocol
        assert callable(validate_IValidatorProtocol)
