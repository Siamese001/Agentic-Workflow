"""Test HygieneGuardianEnhanced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHygieneGuardianEnhanced:
    """Test HygieneGuardianEnhanced functionality."""

    def test_hygiene_guardian_enhanced_imports(self):
        """Test hygiene_guardian_enhanced module imports."""
        from agentic_core import hygiene_guardian_enhanced

        assert hygiene_guardian_enhanced is not None

    def test_hygiene_guardian_enhanced_class(self):
        """Test HygieneGuardianEnhanced class exists."""
        from agentic_core import HygieneGuardianEnhanced

        assert HygieneGuardianEnhanced is not None

    def test_hygiene_guardian_enhanced_callable(self):
        """Test hygiene_guardian_enhanced functions are callable."""
        from agentic_core import validate_hygiene_guardian_enhanced

        assert callable(validate_hygiene_guardian_enhanced)
