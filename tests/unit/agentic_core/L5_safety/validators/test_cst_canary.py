"""Test CstCanary functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCstCanary:
    """Test CstCanary functionality."""

    def test_cst_canary_imports(self):
        """Test cst_canary module imports."""
        from agentic_core import cst_canary

        assert cst_canary is not None

    def test_cst_canary_class(self):
        """Test CstCanary class exists."""
        from agentic_core import CstCanary

        assert CstCanary is not None

    def test_cst_canary_callable(self):
        """Test cst_canary functions are callable."""
        from agentic_core import validate_cst_canary

        assert callable(validate_cst_canary)
