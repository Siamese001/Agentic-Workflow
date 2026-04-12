"""Test FixInheritedInvocationUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFixInheritedInvocationUtil:
    """Test FixInheritedInvocationUtil functionality."""

    def test_fix_inherited_invocation_util_imports(self):
        """Test fix_inherited_invocation_util module imports."""
        from agentic_core import fix_inherited_invocation_util

        assert fix_inherited_invocation_util is not None

    def test_fix_inherited_invocation_util_class(self):
        """Test FixInheritedInvocationUtil class exists."""
        from agentic_core import FixInheritedInvocationUtil

        assert FixInheritedInvocationUtil is not None

    def test_fix_inherited_invocation_util_callable(self):
        """Test fix_inherited_invocation_util functions are callable."""
        from agentic_core import validate_fix_inherited_invocation_util

        assert callable(validate_fix_inherited_invocation_util)
