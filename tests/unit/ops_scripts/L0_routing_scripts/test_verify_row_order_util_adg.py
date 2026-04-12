"""Test VerifyRowOrderUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifyRowOrderUtilAdg:
    """Test VerifyRowOrderUtilAdg functionality."""

    def test_verify_row_order_util_adg_imports(self):
        """Test verify_row_order_util_adg module imports."""
        from agentic_core import verify_row_order_util_adg

        assert verify_row_order_util_adg is not None

    def test_verify_row_order_util_adg_class(self):
        """Test VerifyRowOrderUtilAdg class exists."""
        from agentic_core import VerifyRowOrderUtilAdg

        assert VerifyRowOrderUtilAdg is not None

    def test_verify_row_order_util_adg_callable(self):
        """Test verify_row_order_util_adg functions are callable."""
        from agentic_core import validate_verify_row_order_util_adg

        assert callable(validate_verify_row_order_util_adg)
