"""Test ZeroSsotHardcoding functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestZeroSsotHardcoding:
    """Test ZeroSsotHardcoding functionality."""

    def test_zero_ssot_hardcoding_imports(self):
        """Test zero_ssot_hardcoding module imports."""
        from agentic_core import zero_ssot_hardcoding
        assert zero_ssot_hardcoding is not None

    def test_zero_ssot_hardcoding_class(self):
        """Test ZeroSsotHardcoding class exists."""
        from agentic_core import ZeroSsotHardcoding
        assert ZeroSsotHardcoding is not None

    def test_zero_ssot_hardcoding_callable(self):
        """Test zero_ssot_hardcoding functions are callable."""
        from agentic_core import validate_zero_ssot_hardcoding
        assert callable(validate_zero_ssot_hardcoding)
