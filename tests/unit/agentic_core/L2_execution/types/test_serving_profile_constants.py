"""Test ServingProfileConstants functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestServingProfileConstants:
    """Test ServingProfileConstants functionality."""

    def test_serving_profile_constants_imports(self):
        """Test serving_profile_constants module imports."""
        from agentic_core import serving_profile_constants

        assert serving_profile_constants is not None

    def test_serving_profile_constants_class(self):
        """Test ServingProfileConstants class exists."""
        from agentic_core import ServingProfileConstants

        assert ServingProfileConstants is not None

    def test_serving_profile_constants_callable(self):
        """Test serving_profile_constants functions are callable."""
        from agentic_core import validate_serving_profile_constants

        assert callable(validate_serving_profile_constants)
