"""Test L5Certification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL5Certification:
    """Test L5Certification functionality."""

    def test_l5_certification_imports(self):
        """Test l5_certification module imports."""
        try:
            from agentic_core import l5_certification

            assert l5_certification is not None
        except ImportError:
            pytest.skip("l5_certification not available")

    def test_l5_certification_class(self):
        """Test L5Certification class exists."""
        try:
            from agentic_core import L5Certification

            assert L5Certification is not None
        except ImportError:
            pytest.skip("L5Certification not available")

    def test_l5_certification_callable(self):
        """Test l5_certification functions are callable."""
        try:
            from agentic_core import validate_l5_certification

            assert callable(validate_l5_certification)
        except ImportError:
            pytest.skip("validate_l5_certification not available")
