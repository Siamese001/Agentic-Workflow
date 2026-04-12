"""Test SafetyEnforcementSeam functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafetyEnforcementSeam:
    """Test SafetyEnforcementSeam functionality."""

    def test_safety_enforcement_seam_imports(self):
        """Test safety_enforcement_seam module imports."""
        from agentic_core import safety_enforcement_seam

        assert safety_enforcement_seam is not None

    def test_safety_enforcement_seam_class(self):
        """Test SafetyEnforcementSeam class exists."""
        from agentic_core import SafetyEnforcementSeam

        assert SafetyEnforcementSeam is not None

    def test_safety_enforcement_seam_callable(self):
        """Test safety_enforcement_seam functions are callable."""
        from agentic_core import validate_safety_enforcement_seam

        assert callable(validate_safety_enforcement_seam)
