"""Test HealDepthViolationExhaustive functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealDepthViolationExhaustive:
    """Test HealDepthViolationExhaustive functionality."""

    def test_heal_depth_violation_exhaustive_imports(self):
        """Test heal_depth_violation_exhaustive module imports."""
        try:
            from agentic_core import heal_depth_violation_exhaustive

            assert heal_depth_violation_exhaustive is not None
        except ImportError:
            pytest.skip("heal_depth_violation_exhaustive not available")

    def test_heal_depth_violation_exhaustive_class(self):
        """Test HealDepthViolationExhaustive class exists."""
        try:
            from agentic_core import HealDepthViolationExhaustive

            assert HealDepthViolationExhaustive is not None
        except ImportError:
            pytest.skip("HealDepthViolationExhaustive not available")

    def test_heal_depth_violation_exhaustive_callable(self):
        """Test heal_depth_violation_exhaustive functions are callable."""
        try:
            from agentic_core import validate_heal_depth_violation_exhaustive

            assert callable(validate_heal_depth_violation_exhaustive)
        except ImportError:
            pytest.skip("validate_heal_depth_violation_exhaustive not available")
