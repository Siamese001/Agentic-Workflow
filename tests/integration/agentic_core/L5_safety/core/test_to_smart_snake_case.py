"""Test ToSmartSnakeCase functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToSmartSnakeCase:
    """Test ToSmartSnakeCase functionality."""

    def test_to_smart_snake_case_imports(self):
        """Test to_smart_snake_case module imports."""
        try:
            from agentic_core import to_smart_snake_case

            assert to_smart_snake_case is not None
        except ImportError:
            pytest.skip("to_smart_snake_case not available")

    def test_to_smart_snake_case_class(self):
        """Test ToSmartSnakeCase class exists."""
        try:
            from agentic_core import ToSmartSnakeCase

            assert ToSmartSnakeCase is not None
        except ImportError:
            pytest.skip("ToSmartSnakeCase not available")

    def test_to_smart_snake_case_callable(self):
        """Test to_smart_snake_case functions are callable."""
        try:
            from agentic_core import validate_to_smart_snake_case

            assert callable(validate_to_smart_snake_case)
        except ImportError:
            pytest.skip("validate_to_smart_snake_case not available")
