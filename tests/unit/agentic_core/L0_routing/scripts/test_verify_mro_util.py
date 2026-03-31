"""Test VerifyMroUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifyMroUtil:
    """Test VerifyMroUtil functionality."""

    def test_verify_mro_util_imports(self):
        """Test verify_mro_util module imports."""
        from agentic_core import verify_mro_util
        assert verify_mro_util is not None

    def test_verify_mro_util_class(self):
        """Test VerifyMroUtil class exists."""
        from agentic_core import VerifyMroUtil
        assert VerifyMroUtil is not None

    def test_verify_mro_util_callable(self):
        """Test verify_mro_util functions are callable."""
        from agentic_core import validate_verify_mro_util
        assert callable(validate_verify_mro_util)
