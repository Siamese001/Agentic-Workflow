"""Test GuardianC0Sovereignty functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianC0Sovereignty:
    """Test GuardianC0Sovereignty functionality."""

    def test_guardian_c0_sovereignty_imports(self):
        """Test guardian_c0_sovereignty module imports."""
        from agentic_core import guardian_c0_sovereignty
        assert guardian_c0_sovereignty is not None

    def test_guardian_c0_sovereignty_class(self):
        """Test GuardianC0Sovereignty class exists."""
        from agentic_core import GuardianC0Sovereignty
        assert GuardianC0Sovereignty is not None

    def test_guardian_c0_sovereignty_callable(self):
        """Test guardian_c0_sovereignty functions are callable."""
        from agentic_core import validate_guardian_c0_sovereignty
        assert callable(validate_guardian_c0_sovereignty)
