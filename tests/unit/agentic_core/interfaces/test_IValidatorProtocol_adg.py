"""Test IvalidatorprotocolAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIvalidatorprotocolAdg:
    """Test IvalidatorprotocolAdg functionality."""

    def test_IValidatorProtocol_adg_imports(self):
        """Test IValidatorProtocol_adg module imports."""
        from agentic_core import IValidatorProtocol_adg

        assert IValidatorProtocol_adg is not None

    def test_IValidatorProtocol_adg_class(self):
        """Test IvalidatorprotocolAdg class exists."""
        from agentic_core import IvalidatorprotocolAdg

        assert IvalidatorprotocolAdg is not None

    def test_IValidatorProtocol_adg_callable(self):
        """Test IValidatorProtocol_adg functions are callable."""
        from agentic_core import validate_IValidatorProtocol_adg

        assert callable(validate_IValidatorProtocol_adg)
