"""Test SafetyValidatorsSeam functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafetyValidatorsSeam:
    """Test SafetyValidatorsSeam functionality."""

    def test_safety_validators_seam_imports(self):
        """Test safety_validators_seam module imports."""
        from agentic_core import safety_validators_seam

        assert safety_validators_seam is not None

    def test_safety_validators_seam_class(self):
        """Test SafetyValidatorsSeam class exists."""
        from agentic_core import SafetyValidatorsSeam

        assert SafetyValidatorsSeam is not None

    def test_safety_validators_seam_callable(self):
        """Test safety_validators_seam functions are callable."""
        from agentic_core import validate_safety_validators_seam

        assert callable(validate_safety_validators_seam)
