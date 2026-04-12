"""Test DynamicInvocationAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDynamicInvocationAdg:
    """Test DynamicInvocationAdg functionality."""

    def test_dynamic_invocation_adg_imports(self):
        """Test dynamic_invocation_adg module imports."""
        from agentic_core import dynamic_invocation_adg

        assert dynamic_invocation_adg is not None

    def test_dynamic_invocation_adg_class(self):
        """Test DynamicInvocationAdg class exists."""
        from agentic_core import DynamicInvocationAdg

        assert DynamicInvocationAdg is not None

    def test_dynamic_invocation_adg_callable(self):
        """Test dynamic_invocation_adg functions are callable."""
        from agentic_core import validate_dynamic_invocation_adg

        assert callable(validate_dynamic_invocation_adg)
