"""Test FactoryUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFactoryUtilAdg:
    """Test FactoryUtilAdg functionality."""

    def test_factory_util_adg_imports(self):
        """Test factory_util_adg module imports."""
        from agentic_core import factory_util_adg

        assert factory_util_adg is not None

    def test_factory_util_adg_class(self):
        """Test FactoryUtilAdg class exists."""
        from agentic_core import FactoryUtilAdg

        assert FactoryUtilAdg is not None

    def test_factory_util_adg_callable(self):
        """Test factory_util_adg functions are callable."""
        from agentic_core import validate_factory_util_adg

        assert callable(validate_factory_util_adg)
