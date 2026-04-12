"""Test VerifySelfHealing functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifySelfHealing:
    """Test VerifySelfHealing functionality."""

    def test_verify_self_healing_imports(self):
        """Test verify_self_healing module imports."""
        from agentic_core import verify_self_healing

        assert verify_self_healing is not None

    def test_verify_self_healing_class(self):
        """Test VerifySelfHealing class exists."""
        from agentic_core import VerifySelfHealing

        assert VerifySelfHealing is not None

    def test_verify_self_healing_callable(self):
        """Test verify_self_healing functions are callable."""
        from agentic_core import validate_verify_self_healing

        assert callable(validate_verify_self_healing)
