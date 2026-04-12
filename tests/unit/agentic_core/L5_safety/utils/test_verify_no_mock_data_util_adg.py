"""Test VerifyNoMockDataUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifyNoMockDataUtilAdg:
    """Test VerifyNoMockDataUtilAdg functionality."""

    def test_verify_no_mock_data_util_adg_imports(self):
        """Test verify_no_mock_data_util_adg module imports."""
        from agentic_core import verify_no_mock_data_util_adg

        assert verify_no_mock_data_util_adg is not None

    def test_verify_no_mock_data_util_adg_class(self):
        """Test VerifyNoMockDataUtilAdg class exists."""
        from agentic_core import VerifyNoMockDataUtilAdg

        assert VerifyNoMockDataUtilAdg is not None

    def test_verify_no_mock_data_util_adg_callable(self):
        """Test verify_no_mock_data_util_adg functions are callable."""
        from agentic_core import validate_verify_no_mock_data_util_adg

        assert callable(validate_verify_no_mock_data_util_adg)
